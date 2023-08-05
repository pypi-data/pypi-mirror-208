""" miscellaneous pandas utilities
"""
import numbers

import numpy as np
import pandas as pd

from numtools.intzip import hunzip, hzip


def signed_absmax(df, axis=0, origin=False, mode="max"):
    """retrieve the critical values from a dataframe by series or column,
    keeping correct signed values

    return a series, if origin is False
    return a dataframe if origin is True

    >>> df = pd.DataFrame(
    ...     {"A": [-5, 2, 3], "B": [-2, 0, np.nan], "C": [-6, -2, -9], "D": [1, 4, 0]},
    ...     index=[100, 110, 111],
    ... )
    >>> df
         A    B  C  D
    100 -5 -2.0 -6  1
    110  2  0.0 -2  4
    111  3  NaN -9  0
    >>> signed_absmax(df, axis=1)  # axis=1 by default
    100   -6.0
    110    4.0
    111   -9.0
    Name: crit, dtype: float64
    >>> signed_absmax(df, axis=0)
    A   -5.0
    B   -2.0
    C   -9.0
    D    4.0
    Name: crit, dtype: float64
    >>> signed_absmax(df, axis=0, origin=True)
       crit    orig
    A  -5.0     100
    B  -2.0     100
    C  -9.0     111
    D   4.0     110
    >>> signed_absmax(df, axis=1, origin=True)
         crit   orig
    100  -6.0      C
    110   4.0      D
    111  -9.0      C
    """
    if axis == 0:
        df = df.T
        axis = 1
    f = {"max": np.nanargmax, "min": np.nanargmin}[mode]
    ixs = f(df**2, axis=axis)  # row index if axis=0
    crit = df.values[range(df.shape[0]), ixs]
    index = df.index if axis == 1 else df.columns
    values = pd.Series(crit, index=index, name="crit")
    if origin:
        origin = pd.Series(dict(zip(df.index, df.columns[ixs])), name="orig")
        df = pd.concat((values, origin), axis=1)
        return df
    return values


def subset(df, **levels):
    """easily subset a dataframe based on index
    >>> df = pd.DataFrame({"a": [1, 1, 3], "b": [4, 5, 5], "c": [0, 0, 3.2], "d": [-1, -1, -1]})
    >>> df.set_index(["a", "b"], inplace=True)
    >>> df
           c  d
    a b
    1 4  0.0 -1
      5  0.0 -1
    3 5  3.2 -1
    >>> subset(df, b=5, a=(1,3))
           c  d
    a b
    1 5  0.0 -1
    3 5  3.2 -1
    """
    levels = {k: v for k, v in levels.items() if v is not None}
    if not levels:
        return df
    # handle hszip values
    for k, v in levels.items():
        if isinstance(v, str):
            try:
                v = hunzip(v)
                levels[k] = v
            except:
                pass
    levelnames = df.index.names
    unknown = set(levels.keys()) - set(levelnames)
    if unknown:
        raise ValueError("levels %s do not exist" % unknown)
    # buils a list of filters like:
    # [[allowed values for ix1], allowed values for ix2], etc...]
    filters = []
    # for each index column label
    for levelname in levelnames:
        filter = levels.get(levelname)  # , slice(None))
        if filter is None:
            filters.append(slice(None))
            continue
        elif isinstance(filter, (str, numbers.Number)):
            filters.append([filter])
            continue
        else:
            # pass an enum
            filters.append(filter)
    return df.loc[tuple(filters), :]


def align_df_index(dfs, method="index"):
    """single index/single columns index interpolation alignemnt
    `method`: as per pandas.Dataframe.interpolate `method` parameter

    >>> df1 = pd.DataFrame({"A": [1, 2, 3], "B": [1.1, 2.3, 4.5]}, index=[1.1, 2.01, 3])
    >>> df2 = pd.DataFrame({"A": [1, 2, 3], "B": [1.1, 2.3, 4.5]}, index=[0.9, 1.99, 3.1])
    >>> df1
          A    B
    1.10  1  1.1
    2.01  2  2.3
    3.00  3  4.5
    >>> df2
          A    B
    0.90  1  1.1
    1.99  2  2.3
    3.10  3  4.5
    >>> df1, df2 = align_df_index((df1, df2))
    >>> df1
                 A         B
    0.90       NaN       NaN
    1.10  1.000000  1.100000
    1.99  1.978022  2.273626
    2.01  2.000000  2.300000
    3.00  3.000000  4.500000
    3.10  3.000000  4.500000
    >>> df2
                 A         B
    0.90  1.000000  1.100000
    1.10  1.183486  1.320183
    1.99  2.000000  2.300000
    2.01  2.018018  2.339640
    3.00  2.909910  4.301802
    3.10  3.000000  4.500000
    """
    _dfs = {k: df for k, df in enumerate(dfs)}
    dfs = pd.concat(_dfs, axis=1).sort_index().interpolate(method=method)
    return tuple(dfs[i] for i in dfs.columns.levels[0])


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
