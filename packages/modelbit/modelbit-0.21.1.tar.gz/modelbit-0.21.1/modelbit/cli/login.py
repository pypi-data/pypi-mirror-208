from typing import Optional, Any, Dict

from modelbit.api import MbApi
from modelbit.cli.local_config import saveWorkspaceConfig
from modelbit.cli.ui import output
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


class CloneApi:
  api: MbApi

  def __init__(self, api: MbApi):
    self.api = api

  def checkAuthentication(self) -> Optional[CloneInfo]:
    resp = self.api.getJson("api/cli/v1/clone_info")
    if "errorCode" in resp:
      logger.info(f"Got response {resp}")
      return None
    if isClusterRedirectResponse(resp):
      self.api.setUrls(resp["cluster"])
      return None
    return CloneInfo(resp)


def loginAndPickWorkspace(mbApi: MbApi, source: str, save: bool = False) -> Optional[CloneInfo]:
  cloneInfo = loginAndPickWorkspaceWithApiKey(mbApi, source)
  if cloneInfo is None:
    cloneInfo = loginAndPickWorkspaceWithLoginLink(mbApi, source)
  if cloneInfo is not None and save:
    saveWorkspaceConfig(cloneInfo.workspaceId, cloneInfo.cluster, cloneInfo.gitUserAuthToken)
  return cloneInfo


def apiKeyFromEnv() -> Optional[str]:
  return os.getenv("MB_API_KEY")


def workspaceNameFromEnv() -> Optional[str]:
  return os.getenv("MB_WORKSPACE_NAME")


def loginAndPickWorkspaceWithApiKey(mbApi: MbApi, source: str) -> Optional[CloneInfo]:
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
    cloneInfo = getCloneInfo(mbApi)
    if cloneInfo is None:
      raise Exception("Failed to get cloneInfo")
    return cloneInfo
  except Exception as e:
    logger.info("Error getting token from api key", exc_info=e)
    output(f"Failed to reach login servers for {mbApi.getCluster()}. Please contact support.")
    exit(1)


def loginAndPickWorkspaceWithLoginLink(mbApi: MbApi, source: str) -> Optional[CloneInfo]:
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
    cloneInfo = getCloneInfo(mbApi)
    if cloneInfo:
      break
    triesLeft -= 1
    sleep(3)
  else:
    output("Authentication timed out")

  return cloneInfo


def getCloneInfo(api: MbApi) -> Optional[CloneInfo]:
  resp = api.getJson("api/cli/v1/clone_info")
  if "errorCode" in resp:
    logger.info(f"Got response {resp}")
    return None
  if isClusterRedirectResponse(resp):
    api.setUrls(resp["cluster"])
    return None
  return CloneInfo(resp)


def isClusterRedirectResponse(resp: Dict[str, Any]) -> bool:
  return "cluster" in resp and not "workspaceId" in resp
