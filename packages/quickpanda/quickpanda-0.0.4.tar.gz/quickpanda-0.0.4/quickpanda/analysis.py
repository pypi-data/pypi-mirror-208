import warnings

import numpy as np
from quickpanda.src.file_operate import FileOperator
from quickpanda.src.utils import contain,list_drop


class Analyzer(object):
    def __init__(self,operator:FileOperator):
        self.operator=operator

    def corr_matrix(self,fid,cols=None,method='spearmanr'):
        """
        get correlation between fea
        """
        assert method in ['pearson','spearmanr']
        assert fid in self.operator.dfs.keys()
        if cols is None:
            cols=self.operator.get_cols(fid,'float')
        else:
            assert contain(self.operator.get_cols(fid,'float'),cols)
        if len(cols)<2:
            raise ValueError('at least 2 cols')
        if method=='pearson':
            # return spearmanr(self.operator.dfs[fid].iloc[:,cols])
            return self.operator.dfs[fid].iloc[:,cols].corr()
        else:
            # return spearmanr(self.operator.dfs[fid].iloc[:,cols])
            return self.operator.dfs[fid].iloc[:,cols].corr()

    def corr_unique_values(self,fid,cols=None,index=-1):
        """
        get the data of specific cols,if index !=-1,means x is samples count var.
        return x,y and their col names
        """
        assert fid in self.operator.dfs.keys()
        if cols is None:
            cols=self.operator.get_cols(fid,'float')
        else:
            assert contain(self.operator.get_cols(fid,'float'),cols)
        if index==-1:
            x=np.arange(0,len(self.operator.dfs[fid]))
        else:
            x=self.operator.dfs[fid].iloc[:,index]
        cols=list_drop(cols,index)
        return {
            'x':x.values if index!=-1 else x,
            'y':self.operator.dfs[fid].iloc[:, cols].values,
            'names': {'x':'' if index == -1 else self.operator.dfs[fid].columns[index],'y':self.operator.dfs[fid].columns}
            }

    def corr_unique_groupby(self,fid,by:list,value='mean',cols=None):
        assert len(by)==1
        out=self.corr_multi_groupby(fid,by,value,cols)
        return {
            'by':out['data'][:,0],
            'values':out['data'][:,1:],
            'col_names':out['col_names'],
        }

    def corr_multi_groupby(self,fid,by:list,value='mean',cols=None):

        """
        statistical the difference of value between different groups
        return data[n,len(by+cols)],col_names
        """
        valid_fun={
            'float':['mean', 'std', 'mode', 'min', 'max', 'count'],
            'str':['mode', 'count'],
            'int': ['mode', 'count', 'min', 'max'],
            'func':['mean', 'std', 'mode', 'min', 'max', 'count'],
        }
        assert fid in self.operator.dfs.keys()
        assert contain(self.operator.get_cols(fid,  ['int','str','float']),self.operator.names2idxs(fid,by))

        if not isinstance(value,str):
            warnings.warn('using specific function,please make sure function and cols is correct!')
            allow=['int','str','float']
        else:
            if  value  in ['mode', 'count']:
                allow =['int','str','float']
            elif value in ['min', 'max']:
                allow=['int','float']
            elif value  in ['mean', 'std']:
                allow = ['float']
            else:
                raise ValueError(f'invalid group function:{value}')
        if cols is None:
            cols=self.operator.get_cols(fid,  [allow])
        else:
            if not contain(self.operator.get_cols(fid,  allow),self.operator.names2idxs(fid,cols)):
                raise ValueError(f'the cols to calc {value} should be {allow} dtype')

        g=self.operator.dfs[fid].groupby(by)
        if value=='mode':
            data=g.agg(lambda x: x.value_counts().index[0]).reset_index().loc[:, by + cols]
        else:
            data=g.agg(value).reset_index().loc[:, by + cols]
        return {
            'data':data.values,
            'col_names':by + cols,
            'n_by':len(by)
        }










