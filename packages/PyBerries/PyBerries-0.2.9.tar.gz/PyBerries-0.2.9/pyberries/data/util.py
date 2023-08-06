import numpy as np
import pandas as pd

def dict_val_to_list(dict_in):
    for key, val in dict_in.items():
        dict_in[key] = arg_to_list(val)
    return dict_in

def arg_to_list(arg_in):
    if isinstance(arg_in, list):
        return arg_in
    else:
        return [arg_in]

def set_to_several_objects(in_dict, object_list):
        out_dict = dict()
        for obj, var in in_dict.items():
            if obj.lower() == 'all':
                for key in object_list:
                    out_dict[key] = var
            else:
                out_dict[obj] = var
        return out_dict

def get_histogram(df_in, col, binsize, density:bool=False, drop_duplicates_by=None, groupby:str='Group'):
    bins =  np.arange(df_in[col].min(), df_in[col].max()+2*binsize, binsize)
    df_out = pd.DataFrame(columns=['bins','height',groupby])
    for grp, data in df_in.groupby(groupby, sort=False):
        if drop_duplicates_by:
            data = data.drop_duplicates(subset = drop_duplicates_by)
        df = pd.DataFrame({'bins':bins[:-1]+binsize/2,
                                'height':pd.cut(data[col], bins, include_lowest=True, right=False).value_counts(normalize=density).sort_index(),
                                groupby:grp})
        df_out = pd.concat([df_out, df], axis=0)
    return df_out

def sort_dataframe(df, col:str, order:list=[]):
    def sorter(column):
        cat = pd.Categorical(column, categories=order, ordered=True)
        return pd.Series(cat)
    return df.sort_values(by=col, key=sorter)