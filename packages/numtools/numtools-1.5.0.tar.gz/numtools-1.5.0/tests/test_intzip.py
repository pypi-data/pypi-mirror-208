from numtools import intzip


def test_hunzip_legacy():
    s = "0 to 3, 5 to 9, 11 and 12"
    assert intzip.hunzip(s) == [0, 1, 2, 3, 5, 6, 7, 8, 9, 11, 12]
    femap_output = (
        "         32              ,         45              ,         "
        "47 thru       53, 54              ,      58 ,  ,"
    )
    res = intzip.hunzip(femap_output, linkword="thru")
    assert res == [32, 45, 47, 48, 49, 50, 51, 52, 53, 54, 58]


def test_hunzip():
    s = "0 to 3, 5 THRU 9, 11 AND 12"
    assert intzip.hunzip(s) == [0, 1, 2, 3, 5, 6, 7, 8, 9, 11, 12]
    weird_str = (
        "         32              ,         45              ,         "
        "47 THRU       53, 54              ,      58 upto 61 ,  ,AND 4"
    )
    res = intzip.hunzip(weird_str, sort=False)
    assert res == [32, 45, 47, 48, 49, 50, 51, 52, 53, 54, 58, 59, 60, 61, 4]
    res = intzip.hunzip(weird_str)
    assert res == [4, 32, 45, 47, 48, 49, 50, 51, 52, 53, 54, 58, 59, 60, 61]
