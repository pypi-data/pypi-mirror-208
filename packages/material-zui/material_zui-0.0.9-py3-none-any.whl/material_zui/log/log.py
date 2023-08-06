import logging
from typing import Any, Iterable
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical


def printTable(data: pd.DataFrame | dict[Any, Any] | Iterable[dict[Any, Any]]):
    df = pd.DataFrame(data)
    print(df)
