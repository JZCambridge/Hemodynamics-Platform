import pandas as pd

def readexcel(inpath):
    if 'csv' in inpath:
        DataFrame = pd.read_csv(inpath)
    elif 'xls' in inpath:
        DataFrame = pd.read_excel(inpath)
    else:
        raise ValueError("Cannot open dataframe of: {}".format(inpath))

    return DataFrame