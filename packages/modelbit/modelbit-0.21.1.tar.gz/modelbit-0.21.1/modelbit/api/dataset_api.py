import logging
from typing import Any, Dict, List, Optional

from .api import MbApi

logger = logging.getLogger(__name__)


class OwnerInfo:

  def __init__(self, data: Dict[str, Any]):
    self.id: Optional[str] = data.get("id", None)
    self.name: Optional[str] = data.get("name", None)
    self.imageUrl: Optional[str] = data.get("imageUrl", None)


class DatasetDesc:

  def __init__(self, data: Dict[str, Any]):
    self.name: str = data["name"]
    self.sqlModifiedAtMs: Optional[int] = data.get("sqlModifiedAtMs", None)
    self.query: str = data["query"]
    self.recentResultMs: Optional[int] = data.get("recentResultMs", None)
    self.numRows: Optional[int] = data.get("numRows", None)
    self.numBytes: Optional[int] = data.get("numBytes", None)
    self.ownerInfo = OwnerInfo(data["ownerInfo"])


class ResultDownloadInfo:

  def __init__(self, data: Dict[str, Any]):
    self.id: str = data["id"]
    self.signedDataUrl: str = data["signedDataUrl"]
    self.key64: str = data["key64"]
    self.iv64: str = data["iv64"]


class DatasetApi:
  api: MbApi

  def __init__(self, api: MbApi):
    self.api = api

  def listDatasets(self, branch: str) -> List[DatasetDesc]:
    resp = self.api.getJsonOrThrow("api/cli/v1/datasets/list", {"branch": branch})
    datasets = [DatasetDesc(ds) for ds in resp.get("datasets", [])]
    return datasets

  def getDatasetPkl(self, branch: str, dsName: str) -> Optional[ResultDownloadInfo]:
    resp = self.api.getJsonOrThrow("api/cli/v1/datasets/get", {"branch": branch, "name": dsName})
    if "dsrPklDownloadInfo" in resp:
      return ResultDownloadInfo(resp["dsrPklDownloadInfo"])
    return None

  def getDatasetCsv(self, branch: str, dsName: str) -> Optional[ResultDownloadInfo]:
    resp = self.api.getJsonOrThrow("api/cli/v1/datasets/get", {"branch": branch, "name": dsName})
    if "dsrDownloadInfo" in resp:
      return ResultDownloadInfo(resp["dsrDownloadInfo"])
    return None
