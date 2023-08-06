import os
import random
import pandas as pd
import numpy as np
from pathlib import Path
import time
from multiprocessing import shared_memory
import gzip,io,hashlib
from datetime import datetime
from tqdm import tqdm

from SharedData.Logger import Logger
from SharedData.SharedDataAWSS3 import S3Upload,S3Download,UpdateModTime
from SharedData.SharedDataTableKeys import SharedDataTableKeys
from SharedData.SharedNumpy import SharedNumpy

class SharedDataTable:

    def __init__(self, sharedDataFeeder, dataset, records=None,\
                 names=None,formats=None,size=None):
        self.sharedDataFeeder = sharedDataFeeder
        self.sharedData = self.sharedDataFeeder.sharedData
        self.feeder = self.sharedDataFeeder.feeder
        self.dataset = dataset
        
        self.init_pkey()

        self.create_map = 'na'
        self.init_time = time.time()
        self.download_time = pd.NaT
                        
        # file partitioning threshold
        self.maxtailbytes = int(100*10**6)
        self.minheadbytes = self.maxtailbytes
        # head header
        self.hdrnames = ['headersize','headerdescr','semaphore','md5hash','mtime','itemsize','recordssize','count',\
                         'headsize','pkeysize','minchgid','hastail','descr']
        self.hdrformats = ['<i8','|S250','<u1','|S16','<f8','<i8','<i8','<i8',\
                         '<i8','<i8','<i8','<u1','|S400']
        self.hdrdtype = np.dtype({'names':self.hdrnames,'formats':self.hdrformats})
        self.hdr = np.recarray(shape=(1,), dtype=self.hdrdtype)[0]
        self.hdr['headsize']=0 #initialize headers
        # tail header
        self.tailhdrnames = ['headersize','headerdescr','md5hash','mtime','tailsize']
        self.tailhdrformats = ['<i8','|S80','|S16','<f8','<i8']        
        self.tailhdrdtype = np.dtype({'names':self.tailhdrnames,'formats':self.tailhdrformats})
        self.tailhdr = np.recarray(shape=(1,), dtype=self.tailhdrdtype)[0]
        self.tailhdr['tailsize']=0 #initialize headers
        self.tailhdr['headersize'] = 80
        _headerdescr = ','.join(self.tailhdrnames) +';'+','.join(self.tailhdrformats)
        _headerdescr_b = str.encode(_headerdescr,encoding='UTF-8',errors='ignore')
        self.tailhdr['headerdescr'] = _headerdescr_b
        # primary key hash table
        self.pkey = np.ndarray([])
        self.pkey_initialized = False
        # records
        self.recnames = []
        self.recformats = []
        self.recdtype = None
        self.records = np.ndarray([]) 
        # shared memory
        self.shm = None
        # initalize
        if not names is None:
            self.create(names,formats,size)
        elif records is None: #Read dataset tag
            self.malloc()
        else:
            if isinstance(records,pd.DataFrame):
                records = self.df2records(records)
            self.malloc(records=records)

        self.init_time = time.time() - self.init_time

    def init_pkey(self):

        self.create_pkey_func = None
        self.upsert_func = None
        self.get_loc_func = None

        self.pkeycolumns = SharedDataTableKeys.get_pkeycolumns(self.sharedData.database)

        create_pkey_fname = 'create_pkey_'+str.lower(self.sharedData.database) + '_jit'
        if hasattr(SharedDataTableKeys,create_pkey_fname):
            self.create_pkey_func = getattr(SharedDataTableKeys,create_pkey_fname)
        else:
            raise Exception('create_pkey function not found for database %s!' \
                % (self.sharedData.database))

        upsert_fname = 'upsert_'+str.lower(self.sharedData.database) + '_jit'
        if hasattr(SharedDataTableKeys,upsert_fname):
            self.upsert_func = getattr(SharedDataTableKeys,upsert_fname)
        else:
            raise Exception('upsert function not found for database %s!' \
                % (self.sharedData.database))

        get_loc_fname = 'get_loc_'+str.lower(self.sharedData.database) + '_jit'
        if hasattr(SharedDataTableKeys,get_loc_fname):
            self.get_loc_func = getattr(SharedDataTableKeys,get_loc_fname)
        else:
            raise Exception('get_loc function not found for database %s!' \
                % (self.sharedData.database))
            
    def create(self, names, formats, size):
        path, shm_name = self.get_path(iswrite=True)
        check_pkey = True
        npkeys = len(self.pkeycolumns)
        for k in range(npkeys):
            check_pkey = (check_pkey) & (names[k]==self.pkeycolumns[k])
        if not check_pkey:
            raise Exception('First columns must be %s!' % (self.pkeycolumns))
        else:
            if not 'mtime' in names:
                names.insert(npkeys,'mtime')
                formats.insert(npkeys,'<M8[ns]')
                
            # malloc recarray
            self.recnames = names
            self.rectypes = formats     
            self.recdtype = np.dtype({'names':self.recnames,'formats':self.rectypes})
            pkey_str = ','.join(self.pkeycolumns)
            descr_str = ','.join(self.recnames)+';'+','.join(self.rectypes)+';'+pkey_str
            descr_str_b = str.encode(descr_str,encoding='UTF-8',errors='ignore')
            len_descr = len(descr_str_b)
            
            # build header
            self.hdrnames = ['headersize','headerdescr','semaphore','md5hash','mtime','itemsize','recordssize','count',\
                    'headsize','pkeysize','minchgid','hastail','descr']
            self.hdrformats = ['<i8','|S250','<u1','|S16','<f8','<i8','<i8','<i8',\
                            '<i8','<i8','<i8','<u1','|S'+str(len_descr)]
            hdrnames = ','.join(self.hdrnames)
            hdrdtypes = ','.join(self.hdrformats)
            hdrdescr_str = hdrnames+';'+hdrdtypes
            hdrdescr_str_b = str.encode(hdrdescr_str,encoding='UTF-8',errors='ignore')
                            
            self.hdrdtype = np.dtype({'names':self.hdrnames,'formats':self.hdrformats})
            self.hdr = np.recarray(shape=(1,), dtype=self.hdrdtype)[0]
            self.hdr['headersize']=250
            self.hdr['headerdescr']=hdrdescr_str_b
            self.hdr['mtime'] = datetime.now().timestamp()
            self.hdr['count'] = 0
            self.hdr['minchgid'] = self.hdr['count']
            self.hdr['itemsize'] = int(self.recdtype.itemsize)
            self.hdr['recordssize'] = int(size)
            self.hdr['headsize']=0
            self.hdr['pkeysize']=int(5*size) # around 10% collisions
            self.hdr['descr'] = descr_str_b

            # create memory space                
            self.malloc_create(shm_name)

    def malloc_create(self,shm_name):
        nb_hdr = self.hdrdtype.itemsize # number of header bytes        
        nb_pkey = int(self.hdr['pkeysize']*4) # number of primary key bytes
        nb_records = int(self.hdr['recordssize']*self.hdr['itemsize']) #number of data bytes
        total_size = int(nb_hdr+nb_pkey+nb_records)

        if os.name=='posix':
            try:
                shm = shared_memory.SharedMemory(\
                    name = shm_name,create=False)
                # Release the shared memory
                shm.close()
                shm.unlink()
            except:
                pass

        self.shm = shared_memory.SharedMemory(\
            name=shm_name,create=True,size=total_size)
        
        self.shm.buf[0:nb_hdr] = self.hdr.tobytes()
        self.hdr = np.ndarray((1,),dtype=self.hdrdtype,buffer=self.shm.buf)[0]

        self.pkey = np.ndarray((self.hdr['pkeysize'],),\
            dtype=np.int32,buffer=self.shm.buf,offset=nb_hdr)
        self.pkey[:] = -1

        descr = self.hdr['descr'].decode(encoding='UTF-8',errors='ignore')
        self.recnames = descr.split(';')[0].split(',')
        self.recformats = descr.split(';')[1].split(',')
        self.recdtype = np.dtype({'names':self.recnames,'formats':self.recformats})
        self.records = SharedNumpy((self.hdr['recordssize'],),\
            dtype=self.recdtype,buffer=self.shm.buf, offset=nb_hdr+nb_pkey)
        self.records.master = self
        self.release() # release semaphore       
        
    def malloc(self,records=None, mtime=None):
        tini=time.time()
        
        path, shm_name = self.get_path(iswrite=True)
        # test if shared memory already exists        
        try:
            self.shm = shared_memory.SharedMemory(\
                name = shm_name,create=False)
            self.create_map = 'map'
        except:
            self.create_map = 'create'

        if records is None:
            if self.create_map == 'map':
                self.malloc_map(shm_name)
                return True
            else:
                tini = time.time()
                self.read(path,shm_name)
                te = time.time()-tini+0.000001
                datasize = self.hdr['count']*self.hdr['itemsize']/1000000
                Logger.log.debug('read %s/%s %.2fMB in %.2fs %.2fMBps ' % \
                    (self.feeder,self.dataset,datasize,te,datasize/te))
                return True
        else:            
            if self.create_map == 'map':
                self.malloc_map(shm_name)
            else:
                descr = records.__array_interface__['descr']
                names = [item[0] for item in descr]
                formats = [item[1] for item in descr]
                size = records.size*1.2
                self.create(names,formats,size)                
                self.records.insert(records)
                #self.hdr['minchgid'] = self.records.count

            return True        

    def malloc_map(self, shm_name):
        # Open the shared memory
        self.shm = shared_memory.SharedMemory(name=shm_name, create=False)
        
        # Read the header
        nbhdrdescr = int.from_bytes(self.shm.buf[0:8],byteorder='little')
        hdrdescr_b = self.shm.buf[8:8+nbhdrdescr].tobytes()
        hdrdescr = hdrdescr_b.decode(encoding='UTF-8',errors='ignore')
        hdrdescr = hdrdescr.replace('\x00','')
        self.hdrnames = hdrdescr.split(';')[0].split(',')
        self.hdrformats = hdrdescr.split(';')[1].split(',')
        self.hdrdtype = np.dtype({'names':self.hdrnames,'formats':self.hdrformats})
        nb_hdr = self.hdrdtype.itemsize
        self.hdr = np.ndarray((1,),dtype=self.hdrdtype,buffer=self.shm.buf)[0]

        nb_pkey = int(self.hdr['pkeysize']*4) # number of primary key bytes
        self.pkey = np.ndarray((self.hdr['pkeysize'],),\
            dtype=np.int32,buffer=self.shm.buf,offset=nb_hdr)
        self.pkey_initialized = (self.pkey!=-1).any()
                
        descr = self.hdr['descr'].decode(encoding='UTF-8',errors='ignore')
        self.recnames = descr.split(';')[0].split(',')
        self.recformats = descr.split(';')[1].split(',')
        self.recdtype = np.dtype({'names':self.recnames,'formats':self.recformats})
        self.records = SharedNumpy((self.hdr['recordssize'],),\
            dtype=self.recdtype,buffer=self.shm.buf, offset=nb_hdr+nb_pkey)
        self.records.master = self
            
    def records2df(self,records):                
        df = pd.DataFrame(records, copy=False)
        dtypes = df.dtypes.reset_index()
        dtypes.columns = ['tag','dtype']
        # convert object to string
        string_idx = ['|S' in str(dt) for dt in dtypes['dtype']]
        string_idx = (string_idx) | (dtypes['dtype']=='object')
        tags_obj =  dtypes['tag'][string_idx].values
        for tag in tags_obj:
            try:
                df[tag] = df[tag].str.decode(encoding='utf-8',errors='ignore')
            except:
                pass
        df = df.set_index(self.pkeycolumns)
        return df

    def df2records(self,df):
        check_pkey = True
        if len(self.pkeycolumns) == len(df.index.names):
            for k in range(len(self.pkeycolumns)):
                check_pkey = (check_pkey) & (df.index.names[k]==self.pkeycolumns[k])
        else:
            check_pkey = False
        if not check_pkey:
            raise Exception('First columns must be %s!' % (self.pkeycolumns))
        else:
            if self.recdtype is None:
                df = df.reset_index()
                dtypes = df.dtypes.reset_index()
                dtypes.columns = ['tag','dtype']
                # convert object to string
                tags_obj =  dtypes['tag'][dtypes['dtype']=='object'].values
                for tag in tags_obj:
                    try:
                        df[tag] = df[tag].str.encode(encoding='utf-8',errors='ignore')
                    except:
                        Logger.log.error('Could not convert %s!' % (tag))                        
                    df[tag] = df[tag].astype('|S')        
                return np.ascontiguousarray(df.to_records(index=False))
            else:
                df = df.reset_index()
                dtypes = self.recdtype
                rec = np.full((df.shape[0],),fill_value=np.nan,dtype=dtypes)
                for col in dtypes.names:
                    try:  
                        if col in df.columns:
                            rec[col] = df[col].astype(dtypes[col])
                    except:
                        Logger.log.error('Could not convert %s!' % (col))                                               
                
                return rec
        
    def get_path(self, iswrite=False):
        shm_name = self.sharedData.user + '/' + self.sharedData.database + '/' \
            + self.sharedDataFeeder.feeder + '/' + self.dataset 
        if os.name=='posix':
            shm_name = shm_name.replace('/','\\')
        
        path = Path(os.environ['DATABASE_FOLDER'])
        path = path / self.sharedData.user
        path = path / self.sharedData.database
        path = path / self.sharedDataFeeder.feeder
        path = path / self.dataset        
        path = Path(str(path).replace('\\','/'))
        if self.sharedData.save_local:
            if not os.path.isdir(path):
                os.makedirs(path)
        
        return path, shm_name
    
    def read(self, path, shm_name):
        head_io = None
        head_io_remote_isnewer = False
        tail_io = None
        tail_io_remote_isnewer = False
        headpath = path / 'head.bin'
        tailpath = path / 'tail.bin'
        unzip_head = False

        # open head_io to read header
        # download remote head if its newer than local
        if self.sharedData.s3read:
            force_download= (not self.sharedData.save_local)     
            tini = time.time()
            [head_io_gzip, head_local_mtime, head_remote_mtime] = \
                S3Download(str(headpath),str(headpath)+'.gzip',force_download)            
            if not head_io_gzip is None:
                te = time.time()-tini+0.000001
                datasize = head_io_gzip.getbuffer().nbytes/1000000
                Logger.log.debug('download head %s/%s %.2fMB in %.2fs %.2fMBps ' % \
                    (self.feeder,self.dataset,datasize,te,datasize/te))
                
                head_io_remote_isnewer = True
                head_io_gzip.seek(0)
                head_io = gzip.GzipFile(fileobj=head_io_gzip, mode='rb')                
                unzip_head = True
                
        # open head_io to read header
        if self.sharedData.save_local:
            if head_io is None:
                if headpath.exists():
                    head_io = open(headpath, 'rb')

        # read header
        if not head_io is None:
            head_io.seek(0)
            nbhdrdescr = int.from_bytes(head_io.read(8),byteorder='little')
            hdrdescr_b = head_io.read(nbhdrdescr)
            hdrdescr = hdrdescr_b.decode(encoding='UTF-8',errors='ignore')
            hdrdescr = hdrdescr.replace('\x00','')
            self.hdrnames = hdrdescr.split(';')[0].split(',')
            self.hdrformats = hdrdescr.split(';')[1].split(',')
            self.hdrdtype = np.dtype({'names':self.hdrnames,'formats':self.hdrformats})
            nb_hdr = self.hdrdtype.itemsize            
            head_io.seek(0)
            self.hdr = np.ndarray((1,),dtype=self.hdrdtype,\
                buffer=head_io.read(nb_hdr))[0]
            self.hdr = self.hdr.copy()            
            
            if self.sharedData.s3read:
                if self.hdr['hastail']==1:
                    tini = time.time()
                    [tail_io_gzip, tail_local_mtime, tail_remote_mtime] = \
                        S3Download(str(tailpath),str(tailpath)+'.gzip',force_download)
                    if not tail_io_gzip is None:
                        te = time.time()-tini+0.000001
                        datasize = tail_io_gzip.getbuffer().nbytes/1000000
                        Logger.log.debug('download tail %s/%s %.2fMB in %.2fs %.2fMBps ' % \
                            (self.feeder,self.dataset,datasize,te,datasize/te))
                        
                        tail_io_remote_isnewer = True
                        tail_io_gzip.seek(0)                        
                        tail_io = gzip.GzipFile(fileobj=tail_io_gzip, mode='rb')
             
            if self.sharedData.save_local:
                if self.hdr['hastail']==1:
                    if tail_io is None:                    
                        if tailpath.exists():
                            tail_io = open(tailpath, 'rb')

            # read tail header if exists
            if not tail_io is None:
                tail_io.seek(0)
                tailnbhdrdescr = int.from_bytes(tail_io.read(8),byteorder='little')
                tailhdrdescr_b = tail_io.read(tailnbhdrdescr)
                tailhdrdescr = tailhdrdescr_b.decode(encoding='UTF-8',errors='ignore')
                tailhdrdescr = tailhdrdescr.replace('\x00','')
                self.tailhdrnames = tailhdrdescr.split(';')[0].split(',')
                self.tailhdrformats = tailhdrdescr.split(';')[1].split(',')                
                self.tailhdrdtype = np.dtype({'names':self.tailhdrnames,'formats':self.tailhdrformats})
                                                      
                nbtailhdr = self.tailhdrdtype.itemsize
                tail_io.seek(0)
                tailheader_buf = tail_io.read(nbtailhdr)
                self.tailhdr = np.ndarray((1,),\
                    dtype=self.tailhdrdtype,buffer=tailheader_buf)[0]
                self.tailhdr = self.tailhdr.copy()                 
                self.tailhdr['headersize'] = tailnbhdrdescr     
                self.hdr['count'] = self.hdr['headsize']+self.tailhdr['tailsize']
            
            self.hdr['recordssize'] = int(self.hdr['count']*1.2) # add 20% space for growth
            # malloc create shared memory with recordssize rows
            self.malloc_create(shm_name)            
            nb_pkey = int(self.hdr['pkeysize']*4)
            
            # read head data to shared memory            
            head_io.seek(0)            
            self.shm.buf[0:nb_hdr] = head_io.read(nb_hdr)
            self.hdr['semaphore'] = 1 # force acquire
            
            nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
            nb_head_mb = nb_head / (1000000)
            if nb_head_mb > 50:
                if unzip_head:
                    message = 'Unzipping:%iMB %s/%s' % (nb_head_mb,self.feeder,self.dataset)
                else:
                    message = 'Reading:%iMB %s/%s' % (nb_head_mb,self.feeder,self.dataset)
                block_size = 100 * 1024 * 1024 # or any other block size that you prefer
                # Use a with block to manage the progress bar
                with tqdm(total=nb_head_mb, unit='B',unit_scale=True, desc=message) as pbar:
                    read_bytes = 0
                    # Loop until we have read all the data
                    while read_bytes < nb_head:
                        # Read a block of data
                        chunk_size = min(block_size, nb_head-read_bytes)                        
                        # Update the shared memory buffer with the newly read data
                        self.shm.buf[nb_hdr+nb_pkey+read_bytes:nb_hdr+nb_pkey+read_bytes+chunk_size] = head_io.read(chunk_size)
                        read_bytes += chunk_size # update the total number of bytes read so far
                        # Update the progress bar
                        pbar.update( chunk_size )
            else:
                self.shm.buf[nb_hdr+nb_pkey:nb_hdr+nb_pkey+nb_head] = head_io.read(nb_head)

            # latch the hash value
            md5hash = np.copy(self.hdr['md5hash'])
            if not tail_io is None:
                # replace the hash value with tail value
                md5hash = np.copy(self.tailhdr['md5hash'])
                nb_tail = int(self.tailhdr['tailsize']*self.hdr['itemsize'])
                # read tail data to shared memory
                self.shm.buf[nb_hdr+nb_pkey+nb_head:nb_hdr+nb_pkey+nb_head+nb_tail] = tail_io.read(nb_tail)

            #restore header values
            self.hdr['count'] = self.hdr['headsize']+self.tailhdr['tailsize']
            self.hdr['minchgid'] = self.hdr['count']
            self.hdr['recordssize'] = int(self.hdr['count']*1.2) # add 20% space for growth
            
            # check if data is corrupted            
            nb_records = self.hdr['count']*self.hdr['itemsize']
            self.hdr['md5hash'] = 0
            m = hashlib.md5(self.shm.buf[nb_hdr+nb_pkey:nb_hdr+nb_pkey+nb_records])
            if md5hash != m.digest():
                Logger.log.error('File corrupted %s!' % (path))
                raise Exception('File corrupted %s!' % (path))
            
            self.release()

        if self.sharedData.save_local:
            if (head_io_remote_isnewer) | (tail_io_remote_isnewer):
                try:
                    self.acquire()
                    
                    # create header                
                    [write_head,nb_header,nb_pkey,nb_head,nb_tail] = self.fill_header()
                    # save local
                    if (head_io_remote_isnewer) | (write_head):
                        self.write_head(path,nb_header,nb_pkey,nb_head,head_remote_mtime)
                        UpdateModTime(path/'head.bin',head_remote_mtime)                  
                    if (tail_io_remote_isnewer):
                        self.write_tail(path,nb_header,nb_pkey,nb_head,nb_tail,tail_remote_mtime)
                        UpdateModTime(path/'tail.bin',tail_remote_mtime)
                except Exception as e:
                    Logger.log.error('Could not save local %s\n%s!' % (path,e))
                
                self.release()

        self.release()

    def write(self):
        path, shm_name = self.get_path(iswrite=True)

        try:
            self.acquire()

            tini = time.time()
            # create header
            mtime = self.hdr['mtime']
            [write_head,nb_header,nb_pkey,nb_head,nb_tail] = self.fill_header()
                                        
            # TODO: split write local and remote
            if self.sharedData.s3write:
                if write_head:
                    self.upload_head(path,nb_header,nb_pkey,nb_head,mtime)                
                
                if self.hdr['hastail']==1:        
                    self.upload_tail(path,nb_header,nb_pkey,nb_head,nb_tail,mtime)        
                    
            if self.sharedData.save_local:
                if write_head:
                    self.write_head(path,nb_header,nb_pkey,nb_head,mtime)
                
                if self.hdr['hastail']==1:
                    self.write_tail(path,nb_header,nb_pkey,nb_head,nb_tail,mtime)

            te = time.time()-tini
            datasize = self.hdr['count']*self.hdr['itemsize']/1000000
            Logger.log.debug('write %s/%s %.2fMB in %.2fs %.2fMBps ' % \
                (self.feeder,self.dataset,datasize,te,datasize/te))
        except Exception as e:
            Logger.log.error('Could not write %s\n%s!' % (path,e))
            self.release()
            return False
        
        self.release()
        return True

    def fill_header(self):
        maxtailsize = int(self.maxtailbytes / self.hdr['itemsize'])
        if self.hdr['count']<=maxtailsize:
            tailsize = 0
            headsize = self.hdr['count']            
            self.hdr['hastail']=0
        else:
            tailsize = self.hdr['count'] % maxtailsize            
            headsize = self.hdr['count'] - tailsize
            self.hdr['hastail']=1
        
        
        headsize_chg = (headsize != self.hdr['headsize'])
        self.hdr['headsize'] = headsize

        head_modified = (self.hdr['minchgid']<=self.hdr['headsize'])
        write_head = (head_modified) | (headsize_chg)

        nb_header = int(self.hdrdtype.itemsize)
        nb_pkey = int(self.hdr['pkeysize']*4)        
        nb_head = int(self.hdr['headsize']*self.hdr['itemsize'])
        nb_tail = int(tailsize*self.hdr['itemsize'])
        
        self.tailhdr['mtime'] = self.hdr['mtime']
        self.tailhdr['tailsize'] = tailsize

        self.hdr['md5hash']=0 # reset the hash value        
        m = hashlib.md5(self.shm.buf[nb_header+nb_pkey:nb_header+nb_pkey+nb_head+nb_tail])
        self.hdr['md5hash'] = m.digest()
        self.tailhdr['md5hash'] = self.hdr['md5hash']
        return [write_head,nb_header,nb_pkey,nb_head,nb_tail]
    
    def upload_head(self,path,nb_header,nb_pkey,nb_head,mtime):
        gzip_io = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_io, mode='wb', compresslevel=1) as gz:
            gz.write(self.shm.buf[0:nb_header])
            gz.write(self.shm.buf[nb_header+nb_pkey:nb_header+nb_pkey+nb_head])
        S3Upload(gzip_io,path/'head.bin.gzip',mtime)

    def upload_tail(self,path,nb_header,nb_pkey,nb_head,nb_tail,mtime):
        gzip_io = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_io, mode='wb', compresslevel=1) as gz:
            gz.write(self.tailhdr.tobytes())
            gz.write(self.shm.buf[nb_header+nb_pkey+nb_head:nb_header+nb_pkey+nb_head+nb_tail])
        S3Upload(gzip_io,path/'tail.bin.gzip',mtime)

    def write_head(self,path,nb_header,nb_pkey,nb_head,mtime):
        with open(path/'head.bin', 'wb') as f:
            f.write(self.shm.buf[0:nb_header])
            headsize_mb = nb_head / (1000000)
            blocksize = 1024*1024*100
            descr = 'Writing:%iMB %s/%s' % (headsize_mb,self.feeder,self.dataset)
            if headsize_mb>50:
                with tqdm(total=headsize_mb, unit='B', unit_scale=True, desc=descr) as pbar:
                    written = 0
                    while written < nb_head:
                        chunk_size = min(blocksize, nb_head-written) # write in chunks of max 50 MB size
                        f.write(self.shm.buf[nb_header+nb_pkey+written:nb_header+nb_pkey+written+chunk_size])                                                
                        written += chunk_size
                        pbar.update(chunk_size)
            else:
                f.write(self.shm.buf[nb_header+nb_pkey:nb_header+nb_pkey+nb_head])
            f.flush()
        os.utime(path, (mtime, mtime))
        
    def write_tail(self,path,nb_header,nb_pkey,nb_head,nb_tail,mtime):
        with open(path/'tail.bin', 'wb') as f:
            f.write(self.tailhdr)
            f.write(self.shm.buf[nb_header+nb_pkey+nb_head:nb_header+nb_pkey+nb_head+nb_tail])
            f.flush()
        os.utime(path, (mtime, mtime))
    
    def acquire(self,timeout=5):
        # TODO: ensure that the semaphore is thread safe
        telapsed = 0
        tini = time.time()
        while self.hdr['semaphore']==1:
            tsleep = 0.000001+random.random()/1000000
            telapsed = time.time() - tini
            if telapsed>timeout:
                raise TimeoutError('Timeout waiting for semaphore')
            time.sleep(tsleep)
        self.hdr['semaphore']=1

    def release(self):
        self.hdr['semaphore']=0