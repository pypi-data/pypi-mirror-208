import hashlib
import logging
import os
from typing import Dict, List, Optional

from .api import MbApi

logger = logging.getLogger(__name__)


class PackageDescResponse:
  name: Optional[str] = None
  version: Optional[str] = None
  createdAtMs: Optional[int] = None
  size: Optional[int] = None

  def __init__(self, data: Dict[str, str]):
    if "name" in data:
      self.name = data['name']
    if "version" in data:
      self.version = data['version']
    if "createdAtMs" in data:
      self.createdAtMs = int(data['createdAtMs'])
    if "size" in data:
      self.size = int(data['size'])

  def __repr__(self):
    return f"{self.name}=={self.version}"


class PackageApi:
  api: MbApi

  def __init__(self, api: MbApi):
    self.api = api

  def fetchPackageDesc(self, name: str, version: Optional[str]) -> Optional[PackageDescResponse]:
    resp = self.api.getJsonOrThrow("api/cli/v1/package/info", {"name": name, "pkgversion": version})
    pkgResp = resp.get("package", None)
    pkgDesc = PackageDescResponse(pkgResp) if pkgResp is not None else None
    if pkgDesc:
      logger.info("Found package name=%s version=%s", pkgDesc.name, pkgDesc.version)
    return pkgDesc

  def fetchPackageList(self, name: Optional[str]) -> List[PackageDescResponse]:
    resp = self.api.getJsonOrThrow("api/cli/v1/package/list_all", {"name": name})
    return [PackageDescResponse(pkgResp) for pkgResp in resp.get("packages", [])]

  def deletePackage(self, name: str, version: str) -> Optional[PackageDescResponse]:
    resp = self.api.getJsonOrThrow("api/cli/v1/package/delete", {"name": name, "pkgversion": version})
    pkgResp = resp.get("package", None)
    return PackageDescResponse(pkgResp) if pkgResp is not None else None

  def uploadWheel(self, name: str, version: str, wheelPath: str, allowClobberVersions: bool) -> None:
    with open(wheelPath, 'rb') as f:
      data = f.read()
      contentHash = f"sha1:{hashlib.sha1(data).hexdigest()}"
      self.api.uploadFileOrThrow(
          f"api/cli/v1/package/upload_wheel", {os.path.basename(wheelPath): data},
          dict(name=name,
               version=version,
               contentHash=contentHash,
               allowClobberVersions=str(allowClobberVersions).lower()))
