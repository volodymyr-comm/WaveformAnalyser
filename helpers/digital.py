import pandas as pd


def signal_df_to_change_times_df(data: pd.DataFrame):
    """
    Returns data frame with time of each change of digital signal in columns and multiindex of record & change count number
    """
    _data_df = data.copy()
    # _data_df_changes_mask = _data_df.apply(lambda x: (x != x.shift()))  # count each change of signal
    # _data_df_cnt = _data_df_changes_mask.cumsum()  # count each change of signal
    _data_df = _data_df.apply(lambda x: (x != x.shift()).cumsum())  # count each change of signal
    _data_df.drop_duplicates(inplace=True)  # just to reduce the amount of data
    _data_df = _data_df.groupby(level=0).apply(lambda x: x - x.iloc[0])  # count changes from 0 for each cycle
    _data_df = _data_df.apply(lambda x: x.loc[x != x.shift()])
    _record_col_name, _idx_col_name = _data_df.index.names
    _ret_df = pd.concat(
        [j.reset_index()
         .dropna()
         .rename(columns={i: '_signal_change_no_', _idx_col_name: i})
         .set_index([_record_col_name, '_signal_change_no_'])
         for i, j in _data_df.iteritems()],
        axis='columns')
    return _ret_df
