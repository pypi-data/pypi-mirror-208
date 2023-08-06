from typing import Optional, Any, Dict

from .api import MbApi
from .local_config import saveWorkspaceConfig
from .ui import output
from time import sleep
import logging
import os

logger = logging.getLogger(__name__)


class CloneInfo:

  def __init__(self, data: Dict[str, Any]):
    self.workspaceId: str = data["workspaceId"]
    self.cluster: str = data["cluster"]
    self.gitUserAuthToken: str = data["gitUserAuthToken"]
    self.mbRepoUrl: str = data["mbRepoUrl"]
    self.forgeRepoUrl: Optional[str] = data.get("forgeRepoUrl", None)

  def __str__(self) -> str:
    return str(vars(self))


def loginAndPickWorkspace(mbApi: MbApi, source: str, save: bool = False) -> Optional[CloneInfo]:
  cloneInfo = loginAndPickWorkspaceWithApiKey(mbApi, source, save)
  if cloneInfo is not None:
    return cloneInfo
  return loginAndPickWorkspaceWithLoginLink(mbApi, source, save)


def apiKeyFromEnv() -> Optional[str]:
  return os.getenv("MB_API_KEY")


def workspaceNameFromEnv() -> Optional[str]:
  return os.getenv("MB_WORKSPACE_NAME")


def loginAndPickWorkspaceWithApiKey(mbApi: MbApi, source: str, save: bool) -> Optional[CloneInfo]:
  apiKey = apiKeyFromEnv()
  workspaceName = workspaceNameFromEnv()
  if apiKey is None or workspaceName is None:
    return None
  try:
    if ":" not in apiKey:
      output(f"Incorrect API Key. Please check MB_API_KEY.")
      exit(1)
    logger.info(f"Attempting to log in with API Key {apiKey.split(':')[0]} to workspace {workspaceName}.")
    mbApi.loginWithApiKey(apiKey, workspaceName, source)
    cloneInfo = checkAuthentication(mbApi)
    if not cloneInfo:
      raise Exception("Failed to get cloneInfo")
    if save:
      saveWorkspaceConfig(cloneInfo.workspaceId, cloneInfo.cluster, cloneInfo.gitUserAuthToken)
    return cloneInfo
  except Exception as e:
    logger.info("Error getting token from api key", exc_info=e)
    output(f"Failed to reach login servers for {mbApi.getCluster()}. Please contact support.")
    exit(1)


def loginAndPickWorkspaceWithLoginLink(mbApi: MbApi, source: str, save: bool) -> Optional[CloneInfo]:
  try:
    linkUrl = mbApi.getLoginLink(source)
  except Exception as e:
    logger.info("Error getting login link", exc_info=e)
    output(f"Failed to reach login servers for {mbApi.getCluster()}. Please contact support.")
    exit(1)

  output(f"Authenticate with modelbit: {linkUrl}")

  cloneInfo = None
  triesLeft = 150
  while triesLeft > 0:
    cloneInfo = checkAuthentication(mbApi)
    if cloneInfo:
      break
    triesLeft -= 1
    sleep(3)
  if cloneInfo:
    if save:
      saveWorkspaceConfig(cloneInfo.workspaceId, cloneInfo.cluster, cloneInfo.gitUserAuthToken)
  else:
    output("Authentication timed out")

  return cloneInfo


def checkAuthentication(api: MbApi) -> Optional[CloneInfo]:
  resp = api.getJson("api/cli/v1/login")
  if "errorCode" in resp:
    logger.info(f"Got response {resp}")
    return None
  if isClusterRedirectResponse(resp):
    api.setUrls(resp["cluster"])
    return None
  return CloneInfo(resp)


def isClusterRedirectResponse(resp: Dict[str, Any]) -> bool:
  return "cluster" in resp and not "workspaceId" in resp
