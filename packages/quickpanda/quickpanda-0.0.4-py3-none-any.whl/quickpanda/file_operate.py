import pandas as pd
import numpy as np
import os
import re
from quickpanda.src import utils
from quickpanda.src.utils import get_details,get_cols_desc, format_names,list_in
from quickpanda.src.hyper import FLOATS,INTS,STRS



# pandas read file
def pd_read_csv(path,file_name,sep,show_details):
    df=pd.read_csv(filepath_or_buffer=path,sep=sep)
    df.columns=format_names(df.columns)
    details = get_details(df)
    cols_details=get_cols_desc(df)
    if show_details:
        utils.print_dict_values(details, name='file:' + file_name)
    return df,details,cols_details
def pd_read_excel(path,file_name,sep,show_details):
    df=pd.read_excel(path)
    df.columns=format_names(df.columns)
    details = get_details(df)
    cols_details=get_cols_desc(df)
    if show_details:
        utils.print_dict_values(details, name='file:' + file_name)
    return df,details,cols_details

FILE_FUNC = {
    'csv': pd_read_csv,
    'excel': pd_read_excel,
    'xlsx': pd_read_excel,
    'xls': pd_read_excel,
}
SUPPORT_TYPES={
            'norm':['txt','csv','excel','xlsx','xls'],
            'acc':['pickle','parquet','feather'],
            'extend':['xml','json'],
        }

class FileOperator(object):
    def __init__(self):
        self.df=None
        self.data=None
        self.type=None
        self.io_type=None
        self.support_types=SUPPORT_TYPES
        self.dfs={}
        self.dfs_desc={}
        self.dfs_cols_desc={}

    def read_file(self,fid:str,path:str,file_type='',sep=',',acculate=False,show_detail=False):
        if fid in self.dfs.keys():
            raise ValueError(f'{fid} file exists')
        file_info=path.split('.')
        if file_type=='':
            if len(file_info)<2:
                raise ValueError('unknown file type')
            file_type=file_info[-1]
        file_name=re.split(r'[\/\\\\]',path)[-1]
        is_in,self.io_type,idx= utils.in_dict_lists(self.support_types, value=file_type)
        if not is_in:
            raise ValueError('unsupport file type')
        if not os.path.exists(path):
            raise ValueError(f'file:{path} dont exists')
        if acculate:
            assert self.io_type == 'acc'

        df,details,cols_details=self.pd_read_file(path,file_name,file_type,sep,show_detail)
        self.dfs[fid]=df
        self.dfs_desc[fid]=details
        self.dfs_cols_desc[fid]=cols_details

    def pd_read_file(self,path,file_name,file_type,sep,show_detail):
        return FILE_FUNC[file_type](path,file_name,sep,show_detail)

    def auto_dtype(self,ids=None,default=None):
        if ids is None:
            ids=self.dfs.keys()
        else:
            for i in ids:
                assert i in self.dfs.keys()

        if default is None:
            default={'int':np.int32,'float':np.float32}

        for k in ids:
            for col in self.dfs[k].columns.values:
                if self.dfs[k].dtypes[col] in FLOATS:
                    self.dfs[k][col]=self.dfs[k][col].astype(default['float'])
                elif self.dfs[k].dtypes[col] in INTS:
                    self.dfs[k][col]=self.dfs[k][col].astype(default['int'])
                elif self.dfs[k].dtypes[col] in STRS:
                    self.dfs[k][col]=self.dfs[k][col].astype(np.object)
                else:
                    print(f'unknown type:{self.dfs[k].dtypes[col].dtype}')
            self.dfs_desc[k]=get_details(self.dfs[k])
        print(f'reset dtypes for dfs:{ids}')
    def get_details(self,fids=None):
        if fids is None:
            fids=self.dfs.keys()
        print('file details====================================================================================')
        for i in fids:
            print(f'\t{i}------------')
            for k in self.dfs_desc[i].keys():
                print(f'\t{k}:')
                print(f'\t{self.dfs_desc[i][k]}')

    def asdtype(self,dtypes:dict):

        print('asdtype:\t',end='')
        for f in dtypes.keys():
            if f not in self.dfs.keys():
                raise ValueError(f'not found file {f}')
            print(f'{f}:', end='')
            for c in dtypes[f]:
                if isinstance(c,int):
                    raise ValueError('Only a column name can be used for the key in a dtype mappings argument.')
                if c not in self.dfs[f].columns:
                    raise ValueError(f'not found col {f}.{c}')
                self.dfs[f][c]= self.dfs[f][c].astype(dtypes[f][c])
                print(f'{c}', end=',')
            print(';',end='\t')
            self.dfs_desc[f]=get_details(self.dfs[f])
        print('')

    def get_cols(self,fid,type,name=False):
        if type in ['float','int','str']:
            if not name:
                return self.dfs_desc[fid]['col_dtypes'][type]
            return np.array(self.dfs_desc[fid]['col_names'])[self.dfs_desc[fid]['col_dtypes'][type]]
        else:
            assert list_in(['float','int','str'],type)
            cols=[]
            for t in type:
                cols.extend(self.dfs_desc[fid]['col_dtypes'][t])
            if not name:
                return cols
            else:
                return np.array(self.dfs_desc[fid]['col_names'])[cols]

    def idx2name(self,fid,idx):
        assert idx<len(self.dfs[fid].columns)
        return self.dfs[fid].columns[idx]
    def idxs2names(self,fid,idxs):
        for idx in idxs:
            assert idx<len(self.dfs[fid].columns)
        return self.dfs[fid].columns[idxs]
    def name2idx(self,fid,name):
        return self.dfs_desc[fid]['col_names'].index(name)
    def names2idxs(self,fid,names):
        return [self.name2idx(fid,name) for name in names]


    def save(self):
        pass
    def load(self):
        pass

    def auto_process(self):
        pass

    def df_remove(self,fids):
        for f in fids:
            self.dfs.pop(f)
            self.dfs_desc.pop(f)
            self.dfs_cols_desc.pop(f)

































