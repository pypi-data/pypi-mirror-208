import os,sys
import random
import pandas as pd
import numpy as np
from pathlib import Path
import time
from multiprocessing import shared_memory
import gzip,io,shutil,hashlib,threading
from datetime import datetime
from numba import njit


class SharedDataTableKeys:
    
    def get_pkeycolumns(database):
        if database == 'MarketData':
            return ['date','symbol']
        
        elif database == 'Portfolios':
            return ['date','portfolio']
        
        elif database == 'Risk':
            return ['date','portfolio','riskfactor']
        
        elif database == 'Positions':
            return ['date','portfolio','symbol']
        
        elif database == 'Orders':
            return ['date','portfolio','symbol','clordid']
        
        elif database == 'Trades':
            return ['date','portfolio','symbol','tradeid']
                
        else:
            raise Exception('Database not implemented!')
                
    ############################## NUMBA JIT FUNCTIONS ##############################

    ############################## UPSERT ##############################
    def upsert_single(sharednp,new_record):
        n = sharednp.pkey.size-1
        pkeycolumns=sharednp.master.pkeycolumns
        if sharednp.count < sharednp.size:
            h = hash(new_record[pkeycolumns[0]])
            for key in pkeycolumns[1:]:
                h = h ^ hash(new_record[key])
            h = h % n            
            id = sharednp.pkey[h]
            if id == -1: 
                # new record doesnt exist
                sharednp.pkey[h] = sharednp.count
                sharednp[sharednp.count] = new_record
                sharednp.count = sharednp.count + 1
            else:
                # check for hash collision
                j = 1            
                ismatch = True
                for key in pkeycolumns:
                    ismatch = (ismatch) & (sharednp[id][key] == new_record[key])
                while not ismatch:
                    h = (h + j**2) % n
                    id = sharednp.pkey[h]
                    if id==-1:
                        break
                    ismatch = True
                    for key in pkeycolumns:
                        ismatch = (ismatch) & (sharednp[id][key] == new_record[key])
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    sharednp.pkey[h] = sharednp.count
                    sharednp[sharednp.count] = new_record
                    sharednp.count = sharednp.count + 1
                else:
                    # new record exists                    
                    sharednp[id] = new_record

    @staticmethod
    @njit(cache=True)
    def upsert_marketdata_jit(records,count,new_records,pkey):
        n = pkey.size-1                
        minchgid = count
        maxsize = records.size        
        nrec = new_records.size
        for i in range(nrec):            
            h1 = hash(new_records['date'][i])
            h2 = hash(new_records['symbol'][i])
            h3 = h1 ^ h2
            h = h3 % n            
            id = pkey[h]
            if id == -1: 
                # new record doesnt exist
                pkey[h] = count                
                records[count] = new_records[i]
                if count < maxsize:
                    count = count + 1
                else:
                    break
            else:
                # check for hash collision
                j = 1            
                while (records[id]['date'] != new_records[i]['date'])\
                    | (records[id]['symbol'] != new_records[i]['symbol']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = count                    
                    records[count] = new_records[i]
                    if count < maxsize:
                        count = count + 1
                    else:
                        break
                else:
                    # new record exists                    
                    records[id] = new_records[i]
                    if id < minchgid:
                        minchgid = id
        return count,minchgid
    
    @staticmethod
    @njit(cache=True)
    def upsert_portfolios_jit(records,count,new_records,pkey):
        n = pkey.size-1                
        minchgid = count
        maxsize = records.size        
        nrec = new_records.size
        for i in range(nrec):            
            h1 = hash(new_records['date'][i])
            h2 = hash(new_records['portfolio'][i])
            h3 = h1 ^ h2
            h = h3 % n            
            id = pkey[h]
            if id == -1: 
                # new record doesnt exist
                pkey[h] = count                
                records[count] = new_records[i]
                if count < maxsize:
                    count = count + 1
                else:
                    break
            else:
                # check for hash collision
                j = 1            
                while (records[id]['date'] != new_records[i]['date'])\
                    | (records[id]['portfolio'] != new_records[i]['portfolio']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = count                    
                    records[count] = new_records[i]
                    if count < maxsize:
                        count = count + 1
                    else:
                        break
                else:
                    # new record exists                    
                    records[id] = new_records[i]
                    if id < minchgid:
                        minchgid = id
        return count,minchgid
      
    @staticmethod
    @njit(cache=True)
    def upsert_risk_jit(records,count,new_records,pkey):
        n = pkey.size-1                
        minchgid = count
        maxsize = records.size
        nrec = new_records.size
        for i in range(nrec):            
            h1 = hash(new_records['date'][i])
            h2 = hash(new_records['portfolio'][i])
            h3 = hash(new_records['riskfactor'][i])                
            h4 = h1 ^ h2 ^ h3
            h = h4 % n
            id = pkey[h]
            if id == -1: 
                # new record doesnt exist
                pkey[h] = count                
                records[count] = new_records[i]
                if count < maxsize:
                    count = count + 1
                else:
                    break
            else:
                # check for hash collision
                j = 1                
                while (records[id]['date'] != new_records[i]['date'])\
                    | (records[id]['portfolio'] != new_records[i]['portfolio'])\
                    | (records[id]['riskfactor'] != new_records[i]['riskfactor']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = count
                    records[count] = new_records[i]
                    if count < maxsize:
                        count = count + 1
                    else:
                        break
                else:
                    # new record exists
                    records[id] = new_records[i]
                    if id < minchgid:
                        minchgid = id
        return count,minchgid

    @staticmethod
    @njit(cache=True)
    def upsert_positions_jit(records,count,new_records,pkey):
        n = pkey.size-1                
        minchgid = count
        maxsize = records.size
        nrec = new_records.size
        for i in range(nrec):            
            h1 = hash(new_records['date'][i])
            h2 = hash(new_records['portfolio'][i])
            h3 = hash(new_records['symbol'][i])                
            h4 = h1 ^ h2 ^ h3
            h = h4 % n
            id = pkey[h]
            if id == -1: 
                # new record doesnt exist
                pkey[h] = count                
                records[count] = new_records[i]
                if count < maxsize:
                    count = count + 1
                else:
                    break
            else:
                # check for hash collision
                j = 1                
                while (records[id]['date'] != new_records[i]['date'])\
                    | (records[id]['portfolio'] != new_records[i]['portfolio'])\
                    | (records[id]['symbol'] != new_records[i]['symbol']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = count
                    records[count] = new_records[i]
                    if count < maxsize:
                        count = count + 1
                    else:
                        break
                else:
                    # new record exists
                    records[id] = new_records[i]
                    if id < minchgid:
                        minchgid = id
        return count,minchgid
    
    @staticmethod
    @njit(cache=True)
    def upsert_orders_jit(records,count,new_records,pkey):
        n = pkey.size-1                
        minchgid = count
        maxsize = records.size
        nrec = new_records.size
        for i in range(nrec):            
            h1 = hash(new_records['date'][i])
            h2 = hash(new_records['portfolio'][i])
            h3 = hash(new_records['symbol'][i])
            h4 = hash(new_records['clordid'][i])
            h5 = h1 ^ h2 ^ h3 ^ h4
            h = h5 % n
            id = pkey[h]
            if id == -1: 
                # new record doesnt exist
                pkey[h] = count                
                records[count] = new_records[i]
                if count < maxsize:
                    count = count + 1
                else:
                    break
            else:
                # check for hash collision
                j = 1                
                while (records[id]['date'] != new_records[i]['date'])\
                    | (records[id]['portfolio'] != new_records[i]['portfolio'])\
                    | (records[id]['symbol'] != new_records[i]['symbol'])\
                    | (records[id]['clordid'] != new_records[i]['clordid']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = count
                    records[count] = new_records[i]
                    if count < maxsize:
                        count = count + 1
                    else:
                        break
                else:
                    # new record exists
                    records[id] = new_records[i]
                    if id < minchgid:
                        minchgid = id
        return count,minchgid

    @staticmethod
    @njit(cache=True)
    def upsert_trades_jit(records,count,new_records,pkey):
        n = pkey.size-1                
        minchgid = count
        maxsize = records.size
        nrec = new_records.size
        for i in range(nrec):            
            h1 = hash(new_records['date'][i])
            h2 = hash(new_records['portfolio'][i])
            h3 = hash(new_records['symbol'][i])
            h4 = hash(new_records['tradeid'][i])
            h5 = h1 ^ h2 ^ h3 ^ h4
            h = h5 % n
            id = pkey[h]
            if id == -1: 
                # new record doesnt exist
                pkey[h] = count                
                records[count] = new_records[i]
                if count < maxsize:
                    count = count + 1
                else:
                    break
            else:
                # check for hash collision
                j = 1                
                while (records[id]['date'] != new_records[i]['date'])\
                    | (records[id]['portfolio'] != new_records[i]['portfolio'])\
                    | (records[id]['symbol'] != new_records[i]['symbol'])\
                    | (records[id]['tradeid'] != new_records[i]['tradeid']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = count
                    records[count] = new_records[i]
                    if count < maxsize:
                        count = count + 1
                    else:
                        break
                else:
                    # new record exists
                    records[id] = new_records[i]
                    if id < minchgid:
                        minchgid = id
        return count,minchgid


    ############################# CREATE PKEY #############################  
    @staticmethod
    @njit(cache=True)
    def create_pkey_marketdata_jit(records,count,pkey,start):
        n = pkey.size-1        
        pkey[:] = -1
        for i in range(start,count):
            h1 = hash(records['date'][i])
            h2 = hash(records['symbol'][i])
            h3 = h1 ^ h2
            h = h3 % n            
            id = pkey[h]
            if id == -1:
                pkey[h] = i
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['symbol'] != records[i]['symbol']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = i
                else:
                    raise Exception('error duplicated index!')                    
         
    @staticmethod
    @njit(cache=True)
    def create_pkey_portfolios_jit(records,count,pkey,start):
        n = pkey.size-1        
        pkey[:] = -1
        for i in range(start,count):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = h1 ^ h2
            h = h3 % n            
            id = pkey[h]
            if id == -1:
                pkey[h] = i
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = i
                else:
                    raise Exception('error duplicated index!')                    
            
    @staticmethod
    @njit(cache=True)
    def create_pkey_risk_jit(records,count,pkey,start):
        n = pkey.size-1        
        pkey[:] = -1
        for i in range(start,count):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = hash(records['riskfactor'][i])
            h4 = h1 ^ h2 ^ h3
            h = h4 % n            
            id = pkey[h]
            if id == -1:                 
                pkey[h] = i
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio'])\
                    | (records[id]['riskfactor'] != records[i]['riskfactor']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = i
                else:
                    raise Exception('error duplicated index!')
    
    @staticmethod
    @njit(cache=True)
    def create_pkey_positions_jit(records,count,pkey,start):
        n = pkey.size-1        
        pkey[:] = -1
        for i in range(start,count):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = hash(records['symbol'][i])
            h4 = h1 ^ h2 ^ h3
            h = h4 % n            
            id = pkey[h]
            if id == -1:                 
                pkey[h] = i
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio'])\
                    | (records[id]['symbol'] != records[i]['symbol']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = i
                else:
                    raise Exception('error duplicated index!')                    

    @staticmethod
    @njit(cache=True)
    def create_pkey_orders_jit(records,count,pkey,start):
        n = pkey.size-1        
        pkey[:] = -1
        for i in range(start,count):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = hash(records['symbol'][i])
            h4 = hash(records['clordid'][i])
            h5 = h1 ^ h2 ^ h3 ^ h4
            h = h5 % n            
            id = pkey[h]
            if id == -1:                 
                pkey[h] = i
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio'])\
                    | (records[id]['symbol'] != records[i]['symbol'])\
                    | (records[id]['clordid'] != records[i]['clordid']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = i
                else:
                    raise Exception('error duplicated index!')                    
    
    @staticmethod
    @njit(cache=True)
    def create_pkey_trades_jit(records,count,pkey,start):
        n = pkey.size-1        
        pkey[:] = -1
        for i in range(start,count):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = hash(records['symbol'][i])
            h4 = hash(records['tradeid'][i])
            h5 = h1 ^ h2 ^ h3 ^ h4
            h = h5 % n            
            id = pkey[h]
            if id == -1:                 
                pkey[h] = i
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio'])\
                    | (records[id]['symbol'] != records[i]['symbol'])\
                    | (records[id]['tradeid'] != records[i]['tradeid']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1

                if id == -1: 
                    # new record doesnt exist
                    pkey[h] = i
                else:
                    raise Exception('error duplicated index!')

    ############################# GET LOC #############################
    @staticmethod
    @njit(cache=True)
    def get_loc_marketdata_jit(records,pkey,keys):
        n = pkey.size-1
        loc = np.empty((keys.size, ))
        for i in range(keys.size):
            h1 = hash(keys['date'][i])
            h2 = hash(keys['symbol'][i])
            h3 = h1 ^ h2
            h = h3 % n            
            id = pkey[h]
            if id == -1:
                loc[i] = id
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != keys[i]['date'])\
                    | (records[id]['symbol'] != keys[i]['symbol']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1
                loc[i] = id
        return loc
    
    @staticmethod
    @njit(cache=True)
    def get_loc_portfolios_jit(records,pkey,keys):
        n = pkey.size-1
        loc = np.empty((keys.size, ))
        for i in range(keys.size):
            h1 = hash(keys['date'][i])
            h2 = hash(keys['portfolio'][i])
            h3 = h1 ^ h2
            h = h3 % n            
            id = pkey[h]
            if id == -1:
                loc[i] = id
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != keys[i]['date'])\
                    | (records[id]['portfolio'] != keys[i]['portfolio']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1
                loc[i] = id
        return loc
    
    @staticmethod
    @njit(cache=True)
    def get_loc_risk_jit(records,pkey,keys):
        n = pkey.size-1
        loc = np.empty((keys.size, ))
        for i in range(keys.size):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = hash(records['riskfactor'][i])
            h4 = h1 ^ h2 ^ h3
            h = h4 % n
            id = pkey[h]
            if id == -1:
                loc[i] = id
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio'])\
                    | (records[id]['riskfactor'] != records[i]['riskfactor']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1
                loc[i] = id
        return loc
                
    @staticmethod
    @njit(cache=True)
    def get_loc_positions_jit(records,pkey,keys):
        n = pkey.size-1
        loc = np.empty((keys.size, ))
        for i in range(keys.size):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = hash(records['symbol'][i])
            h4 = h1 ^ h2 ^ h3
            h = h4 % n
            id = pkey[h]
            if id == -1:
                loc[i] = id
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio'])\
                    | (records[id]['symbol'] != records[i]['symbol']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1
                loc[i] = id
        return loc
                        
    @staticmethod
    @njit(cache=True)
    def get_loc_orders_jit(records,pkey,keys):
        n = pkey.size-1
        loc = np.empty((keys.size, ))
        for i in range(keys.size):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = hash(records['symbol'][i])
            h4 = hash(records['clordid'][i])
            h5 = h1 ^ h2 ^ h3 ^ h4
            h = h5 % n
            id = pkey[h]
            if id == -1:
                loc[i] = id
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio'])\
                    | (records[id]['symbol'] != records[i]['symbol'])\
                    | (records[id]['clordid'] != records[i]['clordid']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1
                loc[i] = id
        return loc
    
    @staticmethod
    @njit(cache=True)
    def get_loc_trades_jit(records,pkey,keys):
        n = pkey.size-1
        loc = np.empty((keys.size, ))
        for i in range(keys.size):
            h1 = hash(records['date'][i])
            h2 = hash(records['portfolio'][i])
            h3 = hash(records['symbol'][i])
            h4 = hash(records['tradeid'][i])
            h5 = h1 ^ h2 ^ h3 ^ h4
            h = h5 % n
            id = pkey[h]
            if id == -1:
                loc[i] = id
            else:
                # check for hash collision
                j = 1
                while (records[id]['date'] != records[i]['date'])\
                    | (records[id]['portfolio'] != records[i]['portfolio'])\
                    | (records[id]['symbol'] != records[i]['symbol'])\
                    | (records[id]['tradeid'] != records[i]['tradeid']):
                    h = (h + j**2) % n
                    id = pkey[h]
                    if id==-1:
                        break
                    j += 1
                loc[i] = id
        return loc
                
