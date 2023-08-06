'''
Search for cumulative changes in data.
'''

from tdda import rexpy
import pandas as pd

def _frozenset_target_by_group(df: pd.DataFrame, target: str, group: str) -> pd.DataFrame:
    """
    Groups the values of the target column in df by the corresponding values of
    the group column and returns a new dataframe with a column containing
    frozensets of the grouped values.

    Parameters:
    -----------
    df : pandas.DataFrame
        A pandas DataFrame with columns target and group.
    target : str
        The name of the column to group the values of.
    group : str
        The name of the column to group the values by.

    Returns:
    --------
    pandas.DataFrame
        A new dataframe with a column containing frozensets of the values of
        the target column grouped by the corresponding values of the group
        column.
    """
    # Group target values by corresponding values of group
    grouped = df.groupby(group)[target]\
              .apply(lambda x: frozenset(x))\
              .reset_index(name=target + '_grouped')
    return grouped


def cumrexpy(df: pd.DataFrame, target: str, group: str) -> pd.Series:
    """
    Applies a cumulative extraction of regular expressions to the grouped values
    of the target column in a pandas dataframe.

    Parameters:
    -----------
    df : pandas.DataFrame
        A pandas DataFrame with columns target and group.
    target : str
        The name of the column to group the values of.
    group : str
        The name of the column to group the values by.

    Returns:
    --------
    pandas.Series
        A new series containing the cumulative extraction of regular
        expressions applied to the values of the target column grouped by the
        corresponding values of the group column.
    """
    df_frozen = _frozenset_target_by_group(df, target, group)
    df_frozen = df_frozen.set_index(group)
    result = df_frozen[f'{target}_grouped']\
             .apply(list)\
             .cumsum()\
             .apply(rexpy.extract)
    return result

def df_seq_diff(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a dataframe with rows that have at least one changed value compared to the previous row.

    Parameters:
    -----------
    df : pandas.DataFrame
        A pandas DataFrame with columns to compare for changes.

    Returns:
    --------
    pandas.DataFrame
        A new dataframe containing the rows of the original dataframe that have at least
        one changed value compared to the previous row.
    """
    return df[df != df.shift()]
