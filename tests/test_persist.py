import pandas as pd  # type: ignore

from .utils import persist, sample_df, to_df

_ = persist


def test_read_write_consistency(persist):
    df = sample_df()
    persist.write("fake", df)
    pd.testing.assert_frame_equal(persist.load("fake"), df)


def test_last_index(persist):
    df = sample_df()
    persist.write("fake", df)
    assert persist.last_index("fake") == df.index[-1]


def test_appending_to_cache_given_previous_cache(persist):
    prev = to_df(
        [
            "          , 1 , 2 ",
            "2020-01-01,1.0,2.0",
            "2020-01-02,1.0,2.0",
            "2020-01-05,1.0,2.0",
        ]
    )

    # fmt: off
    new = to_df(
        [
            "          , 2 , 3 ",
            "2020-01-05,   ,2.0",
            "2020-01-06,3.0,3.0",
        ]
    )
    # fmt: on
    expected = to_df(
        [
            "          , 1 , 2 , 3 ",
            "2020-01-01,1.0,2.0,   ",
            "2020-01-02,1.0,2.0,   ",
            "2020-01-05,1.0,   ,2.0",
            "2020-01-06,   ,3.0,3.0",
        ]
    )

    persist.write("fake", prev)
    persist.save("fake", new)
    result = persist.load("fake")
    pd.testing.assert_frame_equal(result, expected)


def test_appending_to_cache_without_previous_cache(persist):
    new = sample_df()
    persist.save("fake", new)
    result = persist.load("fake")
    pd.testing.assert_frame_equal(result, new)


def test_getting_and_setting_cache_version(persist):
    persist.write("fake", sample_df())
    persist.set_version("fake", 10)
    assert persist.version("fake") == 10


def test_int_colume_names(persist):
    df = sample_df()
    df.columns = [int(c) for c in df.columns]
    persist.write("fake", df)
    pd.testing.assert_frame_equal(persist.load("fake"), df)
