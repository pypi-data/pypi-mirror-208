import base64
import os
import re
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
import json

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad

from .utils import boto3Client, inDeployment
from .helpers import getCurrentBranch, getJsonOrPrintError, getDeploymentName


def s3KeyForSecrets(workspaceId: str) -> str:
  return f"{workspaceId}/secrets.json.enc"


def get_secret(name: str,
               deployment: Optional[str] = None,
               branch: Optional[str] = None,
               encoding: str = "utf8") -> str:
  "Defaults to current deployment/branch"
  secretBytes = getSecretFromS3(name, deployment or getDeploymentName() or "", branch or
                                getCurrentBranch()) if inDeployment() else getSecretFromWeb(
                                    name, deployment or "")
  if secretBytes is None:
    raise ValueError(f"Secret not found: {name}")
  return secretBytes.decode(encoding)


def matchesFilter(filterPattern: str, target: str) -> bool:
  return bool(re.match('^' + filterPattern.replace("*", ".*?") + '$', target))


class SecretDesc:
  name: str
  runtimeNameFilter: str
  runtimeBranchFilter: str
  valueEnc64: str
  keyEnc64: str
  iv64: str
  ownerId: str
  createdAtMs: int

  def __init__(self, data: Dict[str, Any]):
    self.name = data['name']
    self.runtimeNameFilter = data['runtimeNameFilter']
    self.runtimeBranchFilter = data['runtimeBranchFilter']
    self.valueEnc64 = data['valueEnc64']
    self.keyEnc64 = data['keyEnc64']
    self.iv64 = data['iv64']
    self.ownerId = data['ownerId']
    self.createdAtMs = data['createdAtMs']

  def __lt__(self, other: "SecretDesc"):
    return len(other.runtimeNameFilter) + len(other.runtimeBranchFilter) < len(self.runtimeNameFilter) + len(
        self.runtimeBranchFilter)

  def decryptedValue(self):
    _pystateKeys = os.getenv('PYSTATE_KEYS')
    for key64 in str(_pystateKeys).split(","):
      cipher = AES.new(base64.b64decode(key64), AES.MODE_ECB)  # type: ignore
      fileKey = unpad(cipher.decrypt(base64.b64decode(self.keyEnc64)), AES.block_size)
      cipher = AES.new(fileKey, AES.MODE_CBC, base64.b64decode(self.iv64))  # type: ignore
      decState = unpad(cipher.decrypt(base64.b64decode(self.valueEnc64)), AES.block_size)
      return decState

  def __repr__(self):
    return str(self.__dict__)

  def matches(self, runtimeName: str, branch: str) -> bool:
    if not len(self.runtimeNameFilter) + len(self.runtimeBranchFilter):
      return True
    return (matchesFilter(self.runtimeBranchFilter, branch) and
            matchesFilter(self.runtimeNameFilter, runtimeName))


def getSecretFromWeb(secretName: str, runtimeName: str) -> Optional[bytes]:
  resp = getJsonOrPrintError("jupyter/v1/secrets/get", dict(secretName=secretName, runtimeName=runtimeName))
  if resp and resp.secretInfo:
    return base64.b64decode(resp.secretInfo.secretValue64)
  return None


def getSecretFromS3(name: str, runtimeName: str, branch: str) -> Optional[bytes]:
  if _secretsFetchedAt is None or datetime.now() - _secretsFetchedAt > timedelta(seconds=300):
    _updateSecretsFromS3()
  _updateSecretsFromS3()

  secrets = _secrets.get(name, [])
  if (len(secrets)) == 0:
    return None

  # Filter to match current runtime
  for secret in secrets:
    if secret.matches(runtimeName=runtimeName, branch=branch):
      return secret.decryptedValue()

  return None


# TODO: Save to disk now that we are reloading?
_secrets: Dict[str, List[SecretDesc]] = {}
_secretsFetchedAt: Optional[datetime] = None


def _updateSecretsFromS3() -> None:
  secrets = _downloadS3Secrets()
  if secrets is None:
    return
  global _secrets, _secretsFetchedAt
  secretDict: Dict[str, List[SecretDesc]] = {}

  for s in (SecretDesc(s) for s in json.loads(secrets)):
    if s.name not in secretDict:
      secretDict[s.name] = []
    secretDict[s.name].append(s)

  for name in secretDict.keys():
    secretDict[name].sort()

  _secrets = secretDict
  _secretsFetchedAt = datetime.now()


def _downloadS3Secrets() -> Optional[str]:
  _workspaceId = os.getenv('WORKSPACE_ID')
  _pystateBucket = os.getenv('PYSTATE_BUCKET')

  if _workspaceId is None or _pystateBucket is None:
    raise Exception(f"EnvVar Missing: WORKSPACE_ID, PYSTATE_BUCKET")
  try:
    s3Key = s3KeyForSecrets(_workspaceId)
    s3Obj = boto3Client('s3').get_object(Bucket=_pystateBucket, Key=s3Key)  # type: ignore
    return s3Obj['Body'].read()  # type: ignore
  except Exception as err:
    strErr = str(err)
    if 'AccessDenied' not in strErr and 'NoSuchKey' not in strErr:
      raise err
  return None
