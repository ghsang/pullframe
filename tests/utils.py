from io import StringIO
from pathlib import Path
from typing import Generator, Iterable

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import pytest  # type: ignore

from pullframe.api import Persist
from pullframe.persist import PERSIST


@pytest.fixture(params=PERSIST.values(), ids=PERSIST.keys())
def persist(tmpdir, request) -> Generator[Persist, None, None]:
    yield request.param.on(Path(tmpdir))


def to_df(csv: Iterable[str]) -> pd.DataFrame:
    csv = StringIO("\n".join(csv))

    df = pd.read_csv(csv, index_col=0, parse_dates=True, na_values=["   "])

    df.columns = [i.strip() for i in df.columns]
    df.index.name = None

    return df


def sample_df() -> pd.DataFrame:
    df = to_df(
        [
            "          ,1, 2 ,3, 4,    5    ,     6     ",
            "2020-01-01,1,   ,2, a,2020-01-01,2020-01-04",
            "2020-01-02,1,   ,2, a,2020-01-02,2020-01-05",
            "2020-01-05,1,1.0,2, a,2020-01-03,2020-01-06",
        ]
    )
    df["3"] = df["3"].astype(np.int32)
    df["5"] = pd.to_datetime(df["5"])
    df["6"] = pd.to_datetime(df["6"]).dt.to_pydatetime()
    return df
