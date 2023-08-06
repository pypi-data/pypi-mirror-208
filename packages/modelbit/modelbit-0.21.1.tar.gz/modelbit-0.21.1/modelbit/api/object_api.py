import logging
from typing import Optional

from .api import MbApi
from ..cli.local_config import getWorkspaceConfig
from ..cli.secure_storage import EncryptedObjectInfo, getSecureData, putSecureData
from ..cli.utils import retry

logger = logging.getLogger(__name__)


class ObjectApi:

  def __init__(self, workspaceId: str, api: Optional[MbApi] = None):
    self.workspaceId = workspaceId
    if api is None:
      config = getWorkspaceConfig(workspaceId)
      # TODO: Do auth dance if config not found
      if not config:
        raise KeyError("workspace config not found")
      api = MbApi(config.gitUserAuthToken, config.cluster)
    self.api = api

  def runtimeObjectUploadUrl(self, contentHash: str) -> EncryptedObjectInfo:
    resp = self.api.getJson("api/cli/v1/runtime_object_upload_url", {
        "contentHash": contentHash,
    })
    return EncryptedObjectInfo(**resp)

  def runtimeObjectDownloadUrl(self, contentHash: str) -> EncryptedObjectInfo:
    resp = self.api.getJson("api/cli/v1/runtime_object_download_url", {
        "contentHash": contentHash,
    })
    return EncryptedObjectInfo(**resp)

  @retry(8, logger)
  def uploadRuntimeObject(self, obj: bytes, contentHash: str, desc: str) -> str:
    resp = self.runtimeObjectUploadUrl(contentHash)
    if resp and not resp.objectExists:
      putSecureData(resp, obj, desc)
    return contentHash

  @retry(8, logger)
  def downloadRuntimeObject(self, contentHash: str, desc: str) -> bytes:
    resp = self.runtimeObjectDownloadUrl(contentHash)
    if not resp or not resp.objectExists:
      raise Exception("Failed to get file URL")
    data = getSecureData(self.workspaceId, resp, desc)
    if not data:
      raise Exception(f"Failed to download and decrypt")
    return data
