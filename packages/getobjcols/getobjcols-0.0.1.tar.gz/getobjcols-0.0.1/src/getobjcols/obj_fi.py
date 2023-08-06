import pandas as pd
def obj_cols(data):
    obj_cols_list=[]
    for col in data.columns:
        if (data[col].dtypes == object):
            print(col)
            obj_cols_list.append(col)
    return obj_cols_list
    