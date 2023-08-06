import pandas as pd
import numpy as np
from quickpanda.src.hyper import FLOATS,INTS,STRS


def drop_cols(df,cols):
    return df.drop(axis=1,columns=cols)

def in_dict_lists(dict:dict=None,value=None):
    if dict is None:
        return None
    is_in,idx,key=False,-1,None
    if value:
        for k in dict.keys():
            if value in dict[k]:
                key=k
                is_in=True
                idx=dict[k].index(value)
    return is_in,key,idx

def print_dict_values(dicts,name):
    print(f'{name} informations:============================================================')
    for k in dicts.keys():
        print(f'{k}:')
        print(dicts[k])

def list_drop(l,value):
    l=list(set(l))
    try:
        l.remove(value)
    except:
        pass
    return l

def list_in(l,values):
    """
    return the indexs of the element of l which in values
    l:
    values:
    """
    return list_drop([i if l[i] in values else -1 for i in range(len(l))],-1)

def contain(fullset,subset):
    """
    if fullset contain subset return 1 else 0
    """
    for i in subset:
        if i not in fullset:
            return 0
    return 1


def get_details(df):
    col_dtypes=list(df.dtypes.values)
    str_cols=list_in(col_dtypes,STRS)
    float_cols=list_in(col_dtypes,FLOATS)
    int_cols=list_in(col_dtypes,INTS)
    return     {
        'base':{'num':len(df),'features_n':len(df.columns.values),},
        'col_names':list(df.columns.values),
        'col_dtypes':{'str':str_cols,'float':float_cols,'int':int_cols},
        'col_null':list(df.isnull().astype(int).sum(axis=0).values),
        'row_null':int(df.isnull().astype(int).any(axis=1).sum()),
               }

def get_cols_desc(df):
    ts={
    'float':['min','max','mode','mean','std'],
    'str':['mode','unique','unique_n'],
    'int':['min','max','mode','unique','unique_n']
    }
    col_dtypes=list(df.dtypes.values)
    col_names=list(df.columns.values)
    str_cols=list_in(col_dtypes,STRS)
    float_cols=list_in(col_dtypes,FLOATS)
    int_cols=list_in(col_dtypes,INTS)
    col_desc={'FLOAT':{},'STR':{},'INT':{}}
    for i in str_cols:
        unique=list(pd.unique(df.iloc[:,i]))
        mode=list(df.iloc[:,i].mode())
        if mode != []:
            mode=mode[0]
        else:
            mode =np.nan
        unique_n=len(unique)
        unique=unique[:1]+['...']+unique[-1:]
        col_desc['STR'][col_names[i]]={'mode':mode,'unique':unique,'unique_n':unique_n,}
    for i in float_cols:
        Min=df.iloc[:,i].min()
        Max=df.iloc[:,i].max()
        Mode=list(df.iloc[:,i].mode())
        if Mode !=[]:
            Mode=Mode[0]
        else:
            Mode =np.nan
        Mean=df.iloc[:,i].mean()
        Std=df.iloc[:,i].std()
        col_desc['FLOAT'][col_names[i]]={'min':Min,'max':Max,'mode':Mode,'mean':Mean,'std':Std}
    for i in int_cols:
        Min=df.iloc[:,i].min()
        Max=df.iloc[:,i].max()
        Mode=list(df.iloc[:,i].mode())
        if Mode !=[]:
            Mode=Mode[0]
        else:
            Mode =np.nan
        unique=list(pd.unique(df.iloc[:,i]))
        unique_n=len(unique)
        unique=unique[:1]+['...']+unique[-1:]
        col_desc['INT'][col_names[i]]={'min':Min,'max':Max,'mode':Mode,'unique':unique,'unique_n':unique_n,}
    return col_desc

def get_files_cols_desc(dfs,fids=None):
    if fids is None:
        fids = dfs.keys()
    files_cols_desc={}
    for i in fids:
        files_cols_desc[i]=get_cols_desc(dfs[i])
    return files_cols_desc

def random_choice(n,indexs):
    assert n<len(indexs)
    return np.random.choice(indexs,size=n)


def format_name(name: str):
    # revise invalid column names
    return name.replace('\n', '_').replace('\t', '').replace(' ', '')
def format_names(names):
    return map(format_name,names)


def set_default_kwarg_2d(l):
    return {
        'title':'',
        'xlabel':'',
        'ylabel':'',
        'xticks':np.arange(l),
        'yticks': np.arange(l),
        'xtickslabel':np.arange(l),
        'ytickslabel':np.arange(l),

        'fs':15,
        'textfs': 15,
        'textc': 'black',
        'marker':['.'],
        'markers':15,

        'figsize':[8,6],
        'legends':[],

    }

def df_flush(df):
    return df.reset_index().drop(['index'], axis=1)




