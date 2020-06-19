# isort:skip_file

from typing import Generator, Iterable

import pandas as pd  # type: ignore

from pullframe.api import Persist

def persist(tmpdir, request) -> Generator[Persist, None, None]: ...
def to_df(csv: Iterable[str]) -> pd.DataFrame: ...
def sample_df() -> pd.DataFrame: ...
