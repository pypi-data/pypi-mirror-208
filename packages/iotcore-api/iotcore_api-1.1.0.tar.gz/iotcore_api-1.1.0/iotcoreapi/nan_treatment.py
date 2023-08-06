import numpy as np
import pandas as pd


def nan_treatment(df: pd.DataFrame, method: str = 'ffill') -> pd.DataFrame:
    """
    NaN treatment for dataframes. Values must be in different columns

    Args:
        df: dataframe in wide format
        method: 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'

    Returns:
        df
    """
    # Cambiar formato de long a wide para correcto análisis por columnas and set timestamp as index
    df.set_index('timeStamp', inplace=True)
    df = df.pivot(columns='uid', values='value')
    numeric_cols = df.select_dtypes(include=np.number).columns
    def interpolate(df):
        if df.index.dtype == 'datetime64[ns]' or df.index.dtype == 'timedelta64[ns]':
            return df.interpolate(method='time')
        else:
            return df.interpolate(method='linear')

    def ffill(df):
        return df.fillna(method='ffill')

    def bfill(df):
        return df.fillna(method='bfill')

    def mean(df):
        return df.fillna(value=df.mean())

    def fill_with_zeros(df):
        return df.fillna(value=0.0)

    switch = {
        'interpolate': df[numeric_cols].interpolate(),
        'bfill': df[numeric_cols].ffill().bfill(),
        'ffill': df[numeric_cols].ffill().bfill(),
        'mean': df[numeric_cols].fillna(value=df.mean()),
        'zerofill': df[numeric_cols].fillna(value=0.0)
    }
    try:
        df[numeric_cols] = switch[method]
        df.reset_index(inplace=True)
        df = df.melt(id_vars=['timeStamp'], var_name='uid', value_name='value')
        return df
    except KeyError:
        raise ValueError("Invalid method. Please use 'interpolate', 'bfill', 'ffill', 'mean', or 'zerofill'.")