import os.path
import warnings

import numpy as np
import tqdm

import seaborn as sns

from quickpanda.src.utils import random_choice
from matplotlib import pyplot as plt
from quickpanda.src.hyper import COLORS,LINESTYLES,MARKERS
from quickpanda.src.utils import contain

default_arg={
    'count':0,
    'max_num':9999,
    'base':{'w':12,'h':10,'dpi':100,'title':'title','xlabel':'xlabel','ylabel':'ylabel'},
    'heatmap':{'w':12,'h':10,'dpi':100,'title':'title','xlabel':'xlabel','ylabel':'ylabel','text_color':'b','text_style':'italic','text_fontsize':15,},
    'linear':{'w':12,'h':10,'dpi':100,'title':'title','xlabel':'xlabel','ylabel':'ylabel','names':None,'linewidth':2,'marker':'','markersize':0, 'markerfacecolor':'red', 'markeredgecolor':'green'},
    'scatter':{'w':12,'h':10,'dpi':100,'title':'title','xlabel':'xlabel','ylabel':'ylabel','names':None,'linewidth':2,'marker':'.','markersize':0, 'markerfacecolor':'red', 'markeredgecolor':'green'},
    'bar':{'w':12,'h':10,'dpi':100,'title':'title','xlabel':'xlabel','ylabel':'ylabel','names':None,'value_labels':[],'edgecolor':'black','scale_group':3,'scale_bar':3,'textfs':10,'xfs':10,'yfs':10,'tfs':10,'text_align':0.3},


}

class fig_ctl(object):
    def __init__(self):
        pass


def auto_size(f_type,shape):
    return [300,300]
def set_arg(default,arg):
    for k in default.keys():
        if k in arg.keys():
            default[k]=arg[k]
    return default

def color_choice(n):
    if n<=COLORS['CSS'][0]:
        return random_choice(n,COLORS['CSS'][1])
    else:
        return random_choice(n,COLORS['XKCD'][1])
def line_choice(n):
    ids=random_choice(n,np.arange(len(LINESTYLES)))
    return np.array(LINESTYLES, dtype=object)[ids]
def marker_choice(n):
    return random_choice(n,MARKERS)
def get_position(width,group_n,var_n,scale_group=1,scale_bar=1):
    """
    给定区域宽度，对组数和变量数给定条件下返回每个变量柱的坐标向量的列表shape=[m,n]
    例如我有一个三个地区的gdp、人口的数据，shape=[3,2]
    scale 是对组和柱的缩放程度，默认scale=1的间距是自身空间的10%，可缩放范围[0.1,9]
    """
    # width,m(group_num),n(var_num)
    w,m,n=width,group_n,var_n
    scale_group=9 if scale_group>9 else scale_group
    scale_group=0.1 if scale_group<0.1 else scale_group
    scale_bar=9 if scale_bar>9 else scale_bar
    scale_bar=0.1 if scale_bar<0.1 else scale_bar
    group_w=w/m
    group_s=scale_group*0.1*group_w
    bar_w=(group_w-group_s)/n
    bar_s=scale_bar*0.1*bar_w
    pos=[]
    for i in range(n):
        pos.append([ group_w*j+bar_w*i+0.5*(group_s+bar_s) for j in range(m)])
    return {
        'pos':np.array(pos),
        'bar_w':bar_w-bar_s,
        # 'group_w':group_w,
        # 'group_s':group_s,
    }

def group_split(group_b,group_w,times):
    split_w=group_w/times
    splits=[]
    for i in range(len(group_b)):
        bias=group_b[i]
        split=[bias+split_w*j for j in range(times)]
        splits.extend(split)
    return {
        "bias":splits,
        "width":split_w
    }

def get_multi_group_position(width, groups, var_n, scale_group=1, scale_bar=1):
    """
    width: total width
    groups:list with num of values each group
    """
    groupsn=[len(g) for g in groups]
    bias = [0]
    w = width
    for g in groupsn[:-1]:
        h = group_split(bias, w, g)
        bias, w = h['bias'], h['width']
    h = get_position(w, groupsn[-1], var_n, scale_group=scale_group, scale_bar=scale_bar)
    posi, bar_w = h['pos'], h['bar_w']
    pos = [posi.T+b for b in bias]
    return {
        'pos': np.vstack(pos),
        'bar_w': bar_w,
    }

def draw_linear(data:np.array,idx=-1,save='',show=False,**arg):
    """
    data:[n,m] n simples and m dimension
    arg:
        w,h.dpi
        names,marker,s,c
    """
    data =np.array(data)
    if len(data.shape)<2:
        data=data.reshape(-1,1)
    arg=set_arg(default_arg['linear'],arg)
    if arg['names'] is None:
        arg['names']=[f'x{i}' for i in range(data.shape[1])]
    n=data.shape[0]
    if idx==-1:
        idx=np.arange(0,n)
    else:
        idx=data[:,idx]
        data=np.hstack([data[:,:idx],data[:,idx+1:]])
        arg['names']=arg['names'].pop(idx)
    m=data.shape[1]
    assert idx.shape[0]==n
    assert m<=len(LINESTYLES)

    plt.figure(figsize=(arg['w'],arg['h']),dpi=arg['dpi'])
    plt.title(arg['title'])
    plt.xlabel(arg['xlabel'])
    plt.ylabel(arg['ylabel'],rotation=0)
    c,styles=color_choice(m),np.array(LINESTYLES,dtype=object)[:m]
    for i in range(m):
        plt.plot(idx,data[:,i],color=c[i], linestyle=tuple(styles[i]),linewidth=arg['linewidth'],marker=arg['marker'],markerfacecolor=arg['markerfacecolor'],markersize=arg['markersize'],markeredgecolor=arg['markeredgecolor'])
    plt.legend(arg['names'])
    if save!='':
        plt.savefig(save)
    if show:
        plt.show()

def univar_linear_plot(dfs,detail,fids=None,cols=None,show=False,path='.',arg=None):
    print('draw linear_plot===============================')
    if fids is None:
        fids = dfs.keys()
    if arg is None:
        arg={}
        for f in fids:
            arg[f]={}
    float_cols={}
    for i in fids:
        float_cols[i]=detail[i]['col_dtypes']['float_cols']
    if cols is None:
        cols={}
        for f in float_cols:
            cols[f]={f'{detail[f]["col_names"][c]}':[-1,c] for c in float_cols[f]}
    if not os.path.exists(path):
        raise ValueError('path dont exists')
    for fid in cols:
        if fid not in fids:
            warnings.warn(f'dfs dont have df: {fid}')
            continue
        save_dir=path+f'/{fid}'
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        for fig in tqdm.tqdm(cols[fid],desc=f'linear plot of {fid} ',total=len(cols[fid])):
                if not contain(float_cols[fid]+[-1],cols[fid][fig]):
                    warnings.warn(f'fig of {fid}/{fig} contain no-float type columns ')
                    continue
                if fig not in arg[fid].keys():
                    arg[fig]={'title':fig,'ylabel':fig,'xlabel':''}
                idx=cols[fid][fig][0]
                used = cols[fid][fig] if idx !=-1 else cols[fid][fig][1:]
                draw_linear(dfs[fid].iloc[:,used],idx=idx,save=save_dir+f'/{fig}.svg',show=show,**arg[fid][fig])

def univar_xlinear_plot(dfs,detail,fids=None,cols=None,show=False,path='.',arg=None):
    print('draw linear_plot===============================')
    if arg is None:
        arg={}
    if fids is None:
        fids = dfs.keys()
    float_cols={}
    for i in fids:
        float_cols[i]=detail[i]['col_dtypes']['float_cols']
    if cols is None:
        cols={}
        for f in float_cols:
            cols[f]={f'{detail[f]["col_names"][c]}':[-1,c] for c in float_cols[f]}
    if not os.path.exists(path):
        raise ValueError('path dont exists')
    for fid in cols:
        if fid not in fids:
            warnings.warn(f'dfs dont have df: {fid}')
            continue
        save_dir=path+f'/{fid}'
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        for fig in tqdm.tqdm(cols[fid],desc=f'linear plot of {fid} ',total=len(cols[fid])):
                if not contain(float_cols[fid]+[-1],cols[fid][fig]):
                    warnings.warn(f'fig of {fid}/{fig} contain no-float type columns ')
                    continue
                if fig not in arg[fid].keys():
                    arg[fig]={'title':fig,'ylabel':fig,'xlabel':''}
                idx=cols[fid][fig][0]
                used = cols[fid][fig] if idx !=-1 else cols[fid][fig][1:]
                draw_linear(dfs[fid].iloc[:,used],idx=idx,save=save_dir+f'/{fig}.svg',show=show,**arg[fid][fig])

# correlation
# corr_heatmap
# corr_scatter
def corr_heatmap(corr_matrix,col_names=None,title=None,path='',save=False,show=False,**kwargs):
    arg=default_arg['base']
    for k in kwargs.keys():
        arg[k]=kwargs[k]
    if col_names is None:
        col_names=range(len(corr_matrix))
    f, ax = plt.subplots(figsize=(len(corr_matrix)+8,len(corr_matrix)+5),dpi=arg['dpi'])
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    sns.heatmap(corr_matrix, cmap=cmap, vmax=1, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True)
    plt.title(title)
    ax.set_xticklabels([plt.Text(i+0.5,0,f'{col_names[i]}') for i in range(len(col_names))], rotation=45)
    ax.set_yticklabels([plt.Text(0,i+0.5,f'{col_names[i]}') for i in range(len(col_names))], rotation=0)
    # for i in range(corr_matrix.shape[0]):
    #     for j in range(corr_matrix.shape[0]):
    #         ax.text(i+0.5,j+0.5,f'{round(corr_matrix[i,j],2)}',style=arg['text_style'],color=arg['text_color'],fontsize=arg['text_fontsize'])
    if save:
        if path!='':
            plt.savefig(path)
    if show:
        plt.show()

def scatter(x,y,xtickslabel=None,path='',save=False,show=False,**kwargs):
    """
    x:the independent var of correlation data np.shape:[n,]
    y:the multi dependent vars of correlation np.shape:[n,m]

    """
    arg=default_arg['scatter']
    for k in kwargs.keys():
        arg[k]=kwargs[k]
    x,y=np.array(x),np.array(y)
    if x.shape[0]!=y.shape[0]:
        y=y.T
    n= y.shape[1]
    if arg['names'] is None:
        arg['names']=[f'c{i}' for i in range(n)]
    colors=color_choice(n)

    fig, ax = plt.subplots(figsize=(arg['w'],arg['h']),dpi=arg['dpi'])
    ax.set_title(arg['title'])
    ax.set_xlabel(arg['xlabel'])
    ax.set_ylabel(arg['ylabel'],rotation=0)
    if xtickslabel is not None:
        ax.set_xticklabels(xtickslabel,rotation=45)

    for i in range(y.shape[1]):
        ax.scatter(x, y[:,i], s=100, c=colors[i], alpha=0.9,marker=arg['marker'],label=arg['names'][i])
    ax.legend()
    if save and path !='':
        plt.savefig(path)
    if show:
        plt.show()

def linear(x,y,xtickslabel=None,path='',save=False,show=False,**kwargs):
    """
    x:the independent var of correlation data np.shape:[n,]
    y:the multi dependent vars of correlation np.shape:[n,m]

    """
    arg=default_arg['linear']
    for k in kwargs.keys():
        arg[k]=kwargs[k]
    x,y=np.array(x),np.array(y)
    if x.shape[0]!=y.shape[0]:
        y=y.T
    n= y.shape[1]
    if arg['names'] is None:
        arg['names']=[f'c{i}' for i in range(n)]
    colors=color_choice(n)
    linestyle=line_choice(n)

    fig, ax = plt.subplots(figsize=(arg['w'],arg['h']),dpi=arg['dpi'])
    ax.set_title(arg['title'])
    ax.set_xlabel(arg['xlabel'])
    ax.set_ylabel(arg['ylabel'],rotation=0)
    if xtickslabel is not None:
        ax.set_xticklabels(xtickslabel,rotation=45)

    for i in range(y.shape[1]):
        ax.plot(x, y[:,i], c=colors[i],label=arg['names'][i],linestyle=tuple(linestyle[i]),linewidth=arg['linewidth'],marker=arg['marker'],markerfacecolor=arg['markerfacecolor'],markersize=arg['markersize'],markeredgecolor=arg['markeredgecolor'])
    ax.legend()
    if save and path !='':
        plt.savefig(path)
    if show:
        plt.show()


def get_idx(i,groupsn):
    idx=[]
    for k in groupsn[::-1]:
        dup=i%k
        idx.append(dup)
        i=(i-dup)//k
    idx.reverse()
    return idx
def group_bar(y,by_n,group_names=None,mark=True,path='',save=False,show=False,**kwargs):
    """
    y:the multi_group_vars  np.shape:[n,m]
    n means group,m means multi_indicators' values
    """
    arg=default_arg['bar']
    for k in kwargs.keys():
        arg[k]=kwargs[k]
    y=np.array(y)
    m,n= y.shape[0],y.shape[1]
    if arg['names'] is None:
        arg['names']=[f'c{i}' for i in range(n)]
    colors=color_choice(n-by_n)
    groups=[]
    groupsn=[]
    total_n=1
    for i in range(by_n):
        groups.append(np.unique(y[:,i]))
        total_n*=len(groups[-1])
        groupsn.append(len(groups[-1]))
    pos=get_multi_group_position(width=arg['w'],groups=groups,var_n=n-by_n,scale_group=arg['scale_group'],scale_bar=arg['scale_bar'])
    fig, ax = plt.subplots(figsize=(arg['w'],arg['h']),dpi=arg['dpi'])
    ax.set_title(arg['title'],fontsize=arg['tfs'])
    ax.set_xlabel(arg['xlabel'],fontsize=arg['xfs'])
    ax.set_ylabel(arg['ylabel'],rotation=0,fontsize=arg['yfs'])
    ax.set_xticks(pos['pos'][:,max((n-by_n)//2,1)])

    xtick_labels=[]
    i,j=0,0
    data=[]
    while i < total_n:
        x=pos['pos'][i,:]
        idx=get_idx(i, groupsn)
        t="_".join([f'{groups[k][idx[k]]}' for k in range(len(idx))])
        xtick_labels.append(t)
        if all([y[j,k]==groups[k][idx[k]] for k in range(len(idx))]):
            u=y[j,by_n:]
            j+=1
        else:
            u=np.zeros([n-by_n])
        data.append(u)
        i+=1
    data=np.vstack(data)
    i=0
    if arg['value_labels']==[]:
        [arg['value_labels'].append(f'value{i}') for i in range(n-by_n)]
    for i in range(n-by_n):
        x=pos['pos'][:,i]
        u=data[:,i]
        ax.bar(x,u,width=pos['bar_w'], color=colors[i],label=arg['value_labels'][i],edgecolor=arg['edgecolor'])
        if mark:
            for k in range(len(x)):
                ax.annotate(f'{round(x[k])}', xy=(x[k], min(u[k]+arg['text_align']*arg['textfs']*k,np.max(u))),
                            xytext=(0, 3), textcoords='offset points', ha='center', va='bottom',fontsize=arg['textfs'])

    if group_names is not None:
        try:
            ax.set_xticklabels(group_names,rotation=45,fontsize=arg['xfs'])
        except:
            print("wrong group_names")
    else:
        ax.set_xticklabels(xtick_labels,rotation=60)

    ax.legend()
    if save and path !='':
        plt.savefig(path)
    if show:
        plt.show()




















































