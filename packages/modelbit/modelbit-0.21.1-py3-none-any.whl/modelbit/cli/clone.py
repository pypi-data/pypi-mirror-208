import logging
import os
import subprocess
import sys
from typing import Optional, Tuple

from modelbit.api import MbApi
from modelbit.cli.login import CloneInfo, loginAndPickWorkspace
from modelbit.cli.ui import chooseOption, output

logger = logging.getLogger(__name__)


def pickGitOrigin(cloneInfo: CloneInfo, origin: Optional[str]) -> Tuple[str, bool]:
  # Origin can be passed in via cmdline. If modelbit, use internal, otherwise use external
  if origin == "modelbit":
    return (cloneInfo.mbRepoUrl, True)
  elif origin is not None:
    if cloneInfo.forgeRepoUrl is None:
      output("Forced external origin but no external repository is configured.")
      exit(1)
    return (cloneInfo.forgeRepoUrl, False)

  if cloneInfo.forgeRepoUrl is None:
    return (cloneInfo.mbRepoUrl, True)

  forgeHost = cloneInfo.forgeRepoUrl.split(":")[0]
  forgeHost = forgeHost.split("@")[1] if forgeHost.index("@") else forgeHost

  action = chooseOption("Choose a remote",
                        [f"Modelbit: {cloneInfo.mbRepoUrl}", f"{forgeHost}: {cloneInfo.forgeRepoUrl}"], 0)
  if action is None:
    output("Nothing chosen")
    exit(1)
  if action.startswith("Modelbit"):
    return (cloneInfo.mbRepoUrl, True)
  return cloneInfo.forgeRepoUrl, False


def doGitClone(workspaceId: str, apiHost: str, gitUrl: str, targetDir: str) -> None:
  cloneConfig = [
      "--config", f"modelbit.restendpoint={apiHost}api/format", "--config",
      "filter.modelbit.process=modelbit gitfilter process", "--config", "filter.modelbit.required",
      "--config", "merge.renormalize=true"
  ]

  env = dict(os.environ.items())
  env["MB_WORKSPACE_ID"] = workspaceId
  logger.info(f"Cloning {gitUrl} into {targetDir} for {workspaceId}")
  try:
    subprocess.run(["git", "clone", *cloneConfig, gitUrl, targetDir],
                   stdin=sys.stdin,
                   stdout=sys.stdout,
                   stderr=sys.stderr,
                   check=True,
                   env=env)
  except subprocess.CalledProcessError:
    output(
        "There was an error cloning your repository. Some large files may not have been restored. Please contact support."
    )


def clone(targetDir: str = "modelbit", origin: Optional[str] = None) -> None:
  if targetDir and os.path.exists(targetDir):
    output(f"Error: Unable to clone repository. The target directory '{targetDir}' already exists.")
    exit(1)

  mbApi = MbApi()
  cloneInfo = loginAndPickWorkspace(mbApi, source="clone", save=True)
  if cloneInfo is None:
    raise Exception("Failed to authenticate. Please try again.")

  gitUrl, _ = pickGitOrigin(cloneInfo, origin)
  doGitClone(cloneInfo.workspaceId, mbApi.getApiHost(), gitUrl, targetDir)
