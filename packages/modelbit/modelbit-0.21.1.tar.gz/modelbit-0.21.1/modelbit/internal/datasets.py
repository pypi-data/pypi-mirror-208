import io
import sqlite3
import tempfile
from typing import Any, Dict, List, Optional, Union, cast

import numpy
import pandas
from modelbit.api import DatasetApi, DatasetDesc, MbApi
from modelbit.helpers import getCurrentBranch, isAuthenticated
from modelbit.secure_storage import (getS3DatasetCsvBytes, getS3DatasetPklBytes, getSecureDataGzip,
                                     getSecureDataZstd)
from modelbit.utils import inDeployment, sizeOfFmt, timeago, timestamp
from modelbit.ux import TableHeader, UserImage, renderTemplate, renderTextTable


# Note cache timeout is for all elements, not per-element
class TimedCache:

  def __init__(self, expireSeconds: int):
    self.expireSeconds = expireSeconds
    self.initTime = timestamp()
    self.cache: Dict[str, Any] = {}

  def maybeResetCache(self):
    if self.initTime + (self.expireSeconds * 1000) < timestamp():
      self.cache = {}
      self.initTime = timestamp()

  def set(self, key: str, val: Any):
    self.maybeResetCache()
    self.cache[key] = val

  def get(self, key: str):
    self.maybeResetCache()
    return self.cache.get(key, None)


class TimedDataframeCache(TimedCache):

  def __init__(self, expireSeconds: int):
    TimedCache.__init__(self, expireSeconds)
    self.cache: Dict[str, pandas.DataFrame] = {}

  def set(self, key: str, val: pandas.DataFrame):
    TimedCache.set(self, key, val)

  def get(self, key: str):
    return cast(Optional[pandas.DataFrame], TimedCache.get(self, key))


class TimedDatabaseCache(TimedCache):

  def __init__(self, expireSeconds: int):
    TimedCache.__init__(self, expireSeconds)
    self.cache: Dict[str, pandas.DataFrame] = {}

  def set(self, key: str, val: sqlite3.Connection):
    TimedCache.set(self, key, val)

  def get(self, key: str):
    return cast(Optional[sqlite3.Connection], TimedCache.get(self, key))


_cacheTimeout = 3
if inDeployment():
  _cacheTimeout = 5 * 60

_dataframeCache = TimedDataframeCache(_cacheTimeout)
_databaseCache = TimedDatabaseCache(_cacheTimeout)


class DatasetList:

  def __init__(self, datasets: List[DatasetDesc]):
    self._datasets: List[DatasetDesc] = []
    self._iter_current = -1
    self._datasets = datasets

  def __repr__(self):
    if not isAuthenticated():
      return ""
    return self._makeDatasetsTable(plainText=True)

  def _repr_html_(self):
    if not isAuthenticated():
      return ""
    return self._makeDatasetsTable()

  def __iter__(self):
    return self

  def __next__(self) -> str:
    self._iter_current += 1
    if self._iter_current < len(self._datasets):
      return self._datasets[self._iter_current].name
    raise StopIteration

  def _makeDatasetsTable(self, plainText: bool = False):
    if len(self._datasets) == 0:
      return "There are no datasets to show."
    headers, rows = self._makeTable()
    if plainText:
      return renderTextTable(headers, rows)
    return renderTemplate("table", headers=headers, rows=rows)

  def _makeTable(self):
    headers = [
        TableHeader("Name", TableHeader.LEFT, isCode=True),
        TableHeader("Owner", TableHeader.CENTER),
        TableHeader("Data Refreshed", TableHeader.RIGHT),
        TableHeader("SQL Updated", TableHeader.RIGHT),
        TableHeader("Rows", TableHeader.RIGHT),
        TableHeader("Bytes", TableHeader.RIGHT),
    ]
    rows: List[List[Union[str, UserImage]]] = []
    for d in self._datasets:
      rows.append([
          d.name,
          UserImage(d.ownerInfo.imageUrl, d.ownerInfo.name),
          timeago(d.recentResultMs) if d.recentResultMs is not None else '',
          timeago(d.sqlModifiedAtMs) if d.sqlModifiedAtMs is not None else '',
          _fmt_num(d.numRows),
          sizeOfFmt(d.numBytes)
      ])
    return (headers, rows)


def list(api: MbApi):
  datasets = DatasetApi(api).listDatasets(getCurrentBranch())
  return DatasetList(datasets)


def _cacheKey(dsName: str):
  return f"{getCurrentBranch()}/{dsName}"


def get(dsName: str,
        filters: Optional[Dict[str, List[Any]]] = None,
        filter_column: Optional[str] = None,
        filter_values: Optional[List[Any]] = None,
        optimize: bool = True,
        mbApi: Optional[MbApi] = None) -> Optional[pandas.DataFrame]:
  if mbApi is None:
    mbApi = MbApi()

  if filter_column is not None and filter_values is not None:
    if filters is None:
      filters = {}
    filters[filter_column] = filter_values

  # loading from CSV is faster when there aren't filters
  if optimize and filters is not None:
    df = _getWithDb(mbApi, dsName, filters)
    if df is not None:
      return df

  df = _getWithCsv(mbApi, dsName, filters)
  if df is None:
    raise Exception(f'Dataset "{dsName}" not found.')
  return df


def _getWithDb(mbApi: MbApi, dsName: str, filters: Optional[Dict[str, List[Any]]] = None):
  ck = _cacheKey(dsName)
  db = _databaseCache.get(ck)
  if db is None:
    if inDeployment():
      db = _getDbFromS3(dsName)
    else:
      db = _getDbFromWeb(mbApi, dsName)
    if db is None:
      return None
  _databaseCache.set(ck, db)
  return _filterDbToDataframe(db, filters)


def _getWithCsv(mbApi: MbApi, dsName: str, filters: Optional[Dict[str, List[Any]]] = None):
  ck = _cacheKey(dsName)
  df = _dataframeCache.get(ck)
  if df is None:
    if inDeployment():
      df = _getDfFromS3(dsName)
    else:
      df = _getDfFromWeb(mbApi, dsName)
  if df is None:
    return None
  _dataframeCache.set(ck, df)
  return _filterDataframe(df, filters)


def _dfFromCsvStream(stream: Optional[bytes]):
  if stream is None:
    return None
  return cast(
      pandas.DataFrame,
      pandas.read_csv(  # type: ignore
          io.BytesIO(stream), sep='|', low_memory=False, na_values=['\\N', '\\\\N']))


def _dbFromPklBytes(stream: Optional[bytes]):
  if stream is None:
    return None
  tempDbFile = tempfile.NamedTemporaryFile()
  tempDbFile.write(stream)
  tempDbFile.flush()
  return sqlite3.connect(tempDbFile.name)


def _filterDataframe(df: pandas.DataFrame, filters: Optional[Dict[str, List[Any]]]):
  if filters is None:
    return df
  for filterCol, filterValues in filters.items():
    df = df[df[filterCol].isin(filterValues)]  # type: ignore
  return df


def _filterDbToDataframe(db: sqlite3.Connection, filters: Optional[Dict[str, List[Any]]]) -> pandas.DataFrame:
  if filters is None:
    df = pandas.read_sql_query(sql="select * from df", con=db)
    convertDbNulls(df)
    return df
  filterGroups: List[str] = []
  filterParams: List[Any] = []
  for filterCol, filterValues in filters.items():
    filterGroup: List[str] = []
    for val in filterValues:
      filterGroup.append(f"`{filterCol}` = ?")
      filterParams.append(val)
    filterGroups.append(f'({" or ".join(filterGroup)})')
  df = pandas.read_sql_query(sql=f"select * from df where {' and '.join(filterGroups)}",
                             params=filterParams,
                             con=db)
  convertDbNulls(df)
  return df


def convertDbNulls(df: pandas.DataFrame):
  df.replace(["\\N", "\\\\N"], numpy.nan, inplace=True)  # type: ignore


def _getDfFromWeb(mbApi: MbApi, dsName: str):
  dsrDownloadInfo = DatasetApi(mbApi).getDatasetCsv(getCurrentBranch(), dsName)
  if dsrDownloadInfo:
    return _dfFromCsvStream(getSecureDataGzip(dsrDownloadInfo, dsName))
  return None


def _getDbFromWeb(mbApi: MbApi, dsName: str):
  dsrPklDownloadInfo = DatasetApi(mbApi).getDatasetPkl(getCurrentBranch(), dsName)
  if dsrPklDownloadInfo:
    return _dbFromPklBytes(getSecureDataZstd(dsrPklDownloadInfo, dsName))
  return None


def _getDfFromS3(dsName: str):
  csvBytes = getS3DatasetCsvBytes(dsName)
  if csvBytes is not None:
    return _dfFromCsvStream(csvBytes)
  return None


def _getDbFromS3(dsName: str):
  pklBytes = getS3DatasetPklBytes(dsName)
  if pklBytes is not None:
    return _dbFromPklBytes(pklBytes)
  return None


def _fmt_num(num: Union[int, Any]):
  if type(num) != int:
    return ""
  return format(num, ",")
