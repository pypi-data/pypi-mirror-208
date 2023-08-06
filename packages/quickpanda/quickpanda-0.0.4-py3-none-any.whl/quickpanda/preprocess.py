import math
import warnings

import matplotlib.pyplot as plt

from quickpanda.src import file_operate
from quickpanda.src.utils import get_details
from quickpanda.src.file_operate import FLOATS
from quickpanda.src.utils import list_in,get_files_cols_desc,get_cols_desc,drop_cols,df_flush

import numpy as np

from sklearn.impute import KNNImputer,SimpleImputer
from sklearn.preprocessing import MinMaxScaler,StandardScaler


def df_drop_outliers(df,cols,draw,path):
    is_drop=[]
    fig, axs=None,None
    ncol,r=3,0
    if len(cols)>30:
        print(f'features num out bounds:{len(cols)}\t',end='')
        draw=False
    if draw:
        r=math.ceil(len(cols)/ncol)
        fig, axs = plt.subplots(r,ncol, figsize=(5 * ncol , 5 * r), dpi=100, gridspec_kw={'wspace':0.4, 'hspace':0.4})
        if r==1:
            axs=[axs]
    for i,col in enumerate(cols):
        q1=df.iloc[:,col].quantile(0.25)
        q3=df.iloc[:,col].quantile(0.75)
        iqr=q3-q1
        outliers= (df.iloc[:,col] < q1 - 1.5*iqr) | (df.iloc[:,col] > q3 + 1.5*iqr)
        d=list(np.argwhere(outliers.values==True).reshape(-1))
        is_drop.extend(d)
        if draw:
            axs[i//ncol][i%ncol].boxplot(df.iloc[:,col], showfliers=True)
            if not df.iloc[:,col].notna().all():
                axs[i // ncol][i % ncol].text(1, 0, 'cnotain Nan values', fontsize=12, ha='center', va='center',c='r')
            axs[i//ncol][i%ncol].set_title(f'out num:{len(d)}')
            axs[i//ncol][i%ncol].set_xticks([])
            axs[i//ncol][i%ncol].set_xticklabels([])
            axs[i//ncol][i%ncol].set_xlabel(f'{df.columns[col]}')
    if draw:
        c=len(cols)%ncol
        if c!=0:
            for i in range(ncol-c):
                axs[r-1][c+i].axis('off')
        if path!='':
            plt.savefig(path)
        plt.show()
    print(f'total drop num:{len(is_drop)}')

    return df_flush(df.drop(list(set(is_drop)),axis=0))
def fillna(dfs,fids, n_neighbors=-1,str_strategy="most_frequent",float_strategy="median",const="",float_miss=np.NaN,str_miss=np.nan):
    if fids is None:
        fids = dfs.keys()
    s_strategys = [ "most_frequent","constant"]
    f_strategys = ["mean", "median"]
    assert float_strategy in f_strategys
    assert str_strategy in s_strategys

    if str_strategy=="constant":
        str_imputer = SimpleImputer(strategy=str_strategy,fill_value=const, missing_values=str_miss)
    else:
        str_imputer = SimpleImputer(strategy=str_strategy, missing_values=str_miss)
    if n_neighbors>0:
        float_imputer = KNNImputer(n_neighbors=n_neighbors)
    else:
        float_imputer = SimpleImputer(strategy=float_strategy, missing_values=float_miss)

    for i in fids:
        df = dfs[i]
        empty_cols,float_cols, str_cols =[], [], []
        for col in dfs[i].columns:
            if int(df.loc[:,col].isnull().astype(int).sum())==len(df):
                empty_cols.append(col)
                continue
            if df.dtypes[col] in FLOATS:
                float_cols.append(col)
            else:
                str_cols.append(col)
        if empty_cols !=[]:
            dfs[i]=drop_cols(df,empty_cols)
            print(f'{i} drop all Nan cols:{empty_cols} ')
        if str_cols!=[]:
            dfs[i].loc[:, str_cols] = str_imputer.fit_transform(dfs[i].loc[:, str_cols].values)
        if float_cols!=[]:
            dfs[i].loc[:, float_cols] = float_imputer.fit_transform(dfs[i].loc[:, float_cols].values)
        dfs[i]=df_flush(dfs[i])
    print(f'fillna for:{list(fids)} ((float_nan={float_miss},strategy:{float_strategy}),(str_nan={str_miss},strategy:{str_strategy}))')
    return dfs
def dropna(dfs,fids=None):
    if fids is None:
        fids = dfs.keys()
    for i in fids:
        dfs[i]=df_flush(dfs[i].dropna())
    print(f'dropna for:{list(fids)}')
    return dfs
def drop_outliers(dfs,detail, fids=None,cols=None,draw=False,path=''):
    if fids is None:
        fids = dfs.keys()
    out_cols={}
    for i in fids:
        out_cols[i]=detail[i]['col_dtypes']['float']
    if cols is None:
        cols=out_cols
    else:
        for i in cols.keys():
            for j in cols[i]:
                if j not in out_cols[i]:
                    print(f'{i}.{j} is not float type, consider col in {out_cols[i]}')
                    return -1
    for i in fids:
        print(i,end='\t')
        dfs[i]=df_drop_outliers(dfs[i],out_cols[i],draw,path)
    return dfs
def norm(dfs,fids=None,cols=None):
    scaler=MinMaxScaler()
    if fids is None:
        fids = dfs.keys()
    float_dtypes={}
    if cols is None:
        for i in fids:
            d=list(dfs[i].dtypes)
            float_dtypes[i]=list_in(d,FLOATS)
    for i in fids:
        dfs[i].iloc[:,float_dtypes[i]]=scaler.fit_transform(dfs[i].iloc[:,float_dtypes[i]])
    print(f'norm float cols for :{float_dtypes}')
    return dfs
def standard(dfs,fids=None,cols=None):
    scaler=StandardScaler()
    if fids is None:
        fids = dfs.keys()
    float_dtypes={}
    if cols is None:
        for i in fids:
            d=list(dfs[i].dtypes)
            float_dtypes[i]=list_in(d,FLOATS)
    for i in fids:
        dfs[i].iloc[:,float_dtypes[i]]=scaler.fit_transform(dfs[i].iloc[:,float_dtypes[i]])
    print(f'standard float cols for :{float_dtypes}')
    return dfs
def show_files_cols_desc(dfs,fids=None):
    files_cols_desc=get_files_cols_desc(dfs,fids)
    print('COLS DESC=======================================================================')
    for file in files_cols_desc.keys():
        print(f'\t{file}----------------------------------------------')
        cols_desc=files_cols_desc[file]
        for k in cols_desc.keys():
            cols=cols_desc[k]
            print(f'\t\t{k}----------')
            for i in cols:
                print(f'\t\t\t{i}:{cols[i]}')
    print('=======================================================================')


class PreProcessor(object):
    def __init__(self, operator: file_operate.FileOperator):
        self.operator=operator

    def update_details(self):
        for i in self.operator.dfs_desc.keys():
            self.operator.dfs_desc[i]=get_details(self.operator.dfs[i])
            self.operator.dfs_cols_desc[i]=get_cols_desc(self.operator.dfs[i])
    def fillna(self,fids=None,n_neighbors=2,str_strategy="most_frequent",float_strategy="mean",const="",float_miss=np.NaN,str_miss=np.nan):

        self.operator.dfs=fillna(self.operator.dfs,fids,n_neighbors,str_strategy,float_strategy,const,float_miss,str_miss)
        self.update_details()
    def dropna(self,fids=None):
        dropna(self.operator.dfs,fids)
        self.update_details()
        self.empty_file_check()
        self.update_details()

    def norm(self,fids=None):
        self.operator.dfs=norm(self.operator.dfs,fids)
        self.update_details()
    def standard(self,fids=None):
        self.operator.dfs=standard(self.operator.dfs,fids)
        self.update_details()
    def regular(self):
        self.update_details()
    def drop_outliers(self,fids=None,cols=None,draw=False,path=''):
        self.operator.dfs=drop_outliers(self.operator.dfs,self.operator.dfs_desc,fids,cols,draw,path)
        self.update_details()
    def show_files_cols_desc(self, fids=None):
        show_files_cols_desc(self.operator.dfs, fids)
    def auto_process(self):
        pass

    def empty_file_check(self):
        drop_ids=[]
        for fid in self.operator.dfs.keys():
            print(self.operator.dfs_desc[fid]['base']['num'])
            if self.operator.dfs_desc[fid]['base']['num']==0:
                drop_ids.append(fid)
        self.operator.df_remove(drop_ids)
        warnings.warn(f'file:{drop_ids} is dropped because is empty')
        self.update_details()











