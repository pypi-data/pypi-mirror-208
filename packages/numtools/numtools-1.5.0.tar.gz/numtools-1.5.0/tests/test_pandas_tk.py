import numpy as np
import pandas as pd
import pytest

from numtools.pandas_tk import signed_absmax, subset


@pytest.fixture
def df():
    df = pd.DataFrame(
        {"A": [-5, 2, 3], "B": [-2, 0, np.nan], "C": [-6, -2, -9], "D": [1, 4, 0]},
        index=[100, 110, 111],
    )
    return df


@pytest.fixture
def df1():
    df = pd.DataFrame(
        {"a": [1, 1, 3], "b": [4, 5, 5], "c": [0, 0, 3.2], "d": [-1, -1, -1]}
    )
    df.set_index(["a", "b"], inplace=True)
    return df


def test_noorigin_axis1(df):
    df_ini = df.copy()
    crit = signed_absmax(df, axis=1)
    expected = pd.Series({100: -6.0, 110: 4.0, 111: -9}, name="crit")
    pd.testing.assert_series_equal(crit, expected)
    # aslo check that initial df has not been modified
    pd.testing.assert_frame_equal(df_ini, df)


def test_noorigin_axis0(df):
    df_ini = df.copy()
    crit = signed_absmax(df, axis=0)
    expected = pd.Series({"A": -5.0, "B": -2.0, "C": -9.0, "D": 4}, name="crit")
    pd.testing.assert_series_equal(crit, expected)
    pd.testing.assert_frame_equal(df_ini, df)


def test_origin_axis1(df):
    df_ini = df.copy()
    crit = signed_absmax(df, axis=1, origin=True)
    expected = pd.DataFrame(
        {
            "crit": {100: -6.0, 110: 4.0, 111: -9.0},
            "orig": {100: "C", 110: "D", 111: "C"},
        }
    )
    pd.testing.assert_frame_equal(crit, expected)
    pd.testing.assert_frame_equal(df_ini, df)


def test_origin_axis0(df):
    df_ini = df.copy()
    crit = signed_absmax(df, axis=0, origin=True)
    expected = pd.DataFrame(
        {
            "crit": {"A": -5.0, "B": -2.0, "C": -9.0, "D": 4.0},
            "orig": {"A": 100, "B": 100, "C": 111, "D": 110},
        }
    )
    pd.testing.assert_frame_equal(crit, expected)
    pd.testing.assert_frame_equal(df_ini, df)


def test_subset_0(df1):
    """check that returned df is not modified when not filter
    is applied"""
    df = subset(df1)
    pd.testing.assert_frame_equal(df, df1)
    df = subset(df1, a=None)
    pd.testing.assert_frame_equal(df, df1)


def test_subset_1(df1):
    df = subset(df1, b=5, a=(1, 3))
    expected = pd.DataFrame(
        {"c": {(1, 5): 0.0, (3, 5): 3.2}, "d": {(1, 5): -1, (3, 5): -1}}
    )
    expected.index.names = ["a", "b"]
    pd.testing.assert_frame_equal(df, expected)


def test_subset_2(df1):
    df = subset(df1, b=5, a="1, 3 TO 10")
    expected = pd.DataFrame(
        {"c": {(1, 5): 0.0, (3, 5): 3.2}, "d": {(1, 5): -1, (3, 5): -1}}
    )
    expected.index.names = ["a", "b"]
    pd.testing.assert_frame_equal(df, expected)
