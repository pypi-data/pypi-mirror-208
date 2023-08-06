import pandas as pd
import numpy as np
import time
from datetime import datetime

from SharedData.Logger import Logger
from SharedData.SharedDataTableKeys import SharedDataTableKeys

class SharedNumpy(np.ndarray):
    
    def __new__(cls, shape, dtype=None, buffer=None, offset=0, strides=None, order=None):
        obj = np.ndarray.__new__(cls, shape, dtype, buffer, offset, strides, order)
        obj.master = None
        return obj
            
    ############################## KEYLESS OPERATIONS ########################################
    
    def insert(self,new_records):
        try:
            self.master.acquire()

            nrec = new_records.size           
            _count = self.count
            if (_count + nrec <= self.size):
                # convert new_records
                if (self.dtype != new_records.dtype):
                    new_records = self.convert(new_records)
                # fill mtime
                nidx = np.isnat(new_records['mtime'])
                if nidx.any():
                    new_records['mtime'][nidx] = time.time_ns()

                arr = super().__getitem__(slice(0, self.size))
                arr[_count:_count+nrec] = new_records
                self.count = _count + nrec            
                self.mtime = datetime.now().timestamp()
            else:
                Logger.log.error('Dataset max size reached!')
        except Exception as e:
            Logger.log.error('Error inserting records!\n%s' % (e))

        self.master.release()

    def overwrite(self,new_records):
        try:
            self.master.acquire()

            # assume new_records is sorted 
            # overwrite based on the first date
            if isinstance(new_records,pd.DataFrame):
                new_records = self.master.df2records(new_records)
            elif (self.dtype != new_records.dtype):
                new_records = self.convert(new_records)
            # fill mtime
            nidx = np.isnat(new_records['mtime'])
            if nidx.any():
                new_records['mtime'][nidx] = time.time_ns()

            nrec = new_records.size
            _count = self.count
            # overwrite from first date
            fdate = new_records[0]['date']
            fdateid = np.where(self['date']>=fdate)[0]
            if np.any(fdateid):
                _count = fdateid[0]
            # set data
            if (_count + nrec <= self.size):                        
                arr = super().__getitem__(slice(0, self.size))
                arr[_count:_count+nrec] = new_records
                self.count = _count + nrec
                self.minchgid = _count
                self.mtime = datetime.now().timestamp()
            else:
                Logger.log.error('Dataset max size reached!')
        except Exception as e:
            Logger.log.error('Error overwriting records!\n%s' % (e))

        self.master.release()

    ############################## PRIMARY KEY OPERATIONS ########################################
    
    def create_pkey(self,start=0):
        arr = super().__getitem__(slice(0, self.size))
        self.master.create_pkey_func(arr,self.count,self.pkey,start)        
        if start==0:
            self.pkey_initialized = True

    def upsert(self,new_records):
        try:
            self.master.acquire()        
            
            if not self.pkey_initialized:
                self.create_pkey()

            if isinstance(new_records,pd.DataFrame):
                new_records = self.master.df2records(new_records)
            elif (self.dtype != new_records.dtype):
                new_records = self.convert(new_records)

            # fill mtime
            nidx = np.isnat(new_records['mtime'])
            if nidx.any():
                new_records['mtime'][nidx] = time.time_ns()

            minchgid = self.count        
            if new_records.shape==():
                SharedDataTableKeys.upsert_single(self,new_records)
            else:            
                arr = super().__getitem__(slice(0, self.size))
                self.count,minchgid = self.master.upsert_func(arr,self.count,new_records,self.pkey)

            if self.count == self.size:
                Logger.log.warning('Dataset %s/%s is full!' % \
                    (self.master.feeder,self.master.dataset))

            self.minchgid = minchgid
            self.mtime = datetime.now().timestamp()
        except Exception as e:
            Logger.log.error('Error upserting records!\n%s' % (e))

        self.master.release()
        return minchgid
            
    def get_loc(self,keys):
        try:
            self.master.acquire()
            if not self.pkey_initialized:
                self.create_pkey()  
            loc = self.master.get_loc_func(self[:],self.pkey,keys).astype(int)
        except Exception as e:
            Logger.log.error('Error getting loc!\n%s' % (e))
            loc = np.array([])
        self.master.release()
        return loc
                
    def sort_index(self,start=0):
        try:
            self.master.acquire()

            # TODO: generalize to multiple keys
            keys = tuple(self[column][start:] for column in self.master.pkeycolumns[::-1])
            idx = np.lexsort(keys)
            
            shift_idx = np.roll(idx, 1)
            if len(shift_idx)>0:
                shift_idx[0] = -1
                idx_diff = idx - shift_idx
                unsortered_idx = np.where(idx_diff != 1)[0]
                if np.where(idx_diff != 1)[0].any():
                    _minchgid = np.min(unsortered_idx) + start
                    self.minchgid = _minchgid
                    self[start:] = self[start:][idx]
                    if not self.pkey_initialized:
                        self.create_pkey()
                    else:
                        self.create_pkey(_minchgid)
        except Exception as e:
            Logger.log.error('Error sorting index!\n%s' % (e))

        self.master.release()

    def write(self):
        self.master.write()

    def records2df(self,records):
        return self.master.records2df(records)
    
    def convert(self,new_records):
        rec = np.full((new_records.size,),fill_value=np.nan,dtype=self.dtype)        
        for col in self.dtype.names:
            if col in new_records.dtype.names:
                try:
                    rec[col] = new_records[col].astype(self.dtype[col])
                except:
                    Logger.log.error('Could not convert %s!' % (col))
        return rec

    ############################## GETTERS / SETTERS ##############################
    
    def __getitem__(self, key):
        if hasattr(self,'master'):
            if self.count>0:
                arr = super().__getitem__(slice(0, self.count)) # slice arr
                return arr.__getitem__(key)
            else:
                return np.array([])
        else:
            return super().__getitem__(key)
        
    @property
    def count(self):
        return self.master.hdr['count']
    
    @count.setter
    def count(self,value):
        self.master.hdr['count'] = value
    
    @property
    def mtime(self):
        return self.master.hdr['mtime']
    
    @mtime.setter
    def mtime(self,value):
        self.master.hdr['mtime'] = value

    @property
    def minchgid(self):
        return self.master.hdr['minchgid']
    
    @minchgid.setter
    def minchgid(self,value):
        value = min(value,self.master.hdr['minchgid'])
        self.master.hdr['minchgid'] = value
            
    @property
    def pkey(self):
        return self.master.pkey
    
    @pkey.setter
    def pkey(self,value):        
        self.master.pkey = value
    
    @property
    def pkey_initialized(self):
        return self.master.pkey_initialized
    
    @pkey_initialized.setter
    def pkey_initialized(self,value):        
        self.master.pkey_initialized = value