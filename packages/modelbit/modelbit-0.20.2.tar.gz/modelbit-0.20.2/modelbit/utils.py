from typing import Union, Any, cast, Dict, Callable, Tuple, Optional
from datetime import datetime
import os, pickle, gzip, hashlib, re
import time

_deserializeCache: Dict[str, Any] = {}


# From https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeOfFmt(num: Union[int, Any]):
  if type(num) != int:
    return ""
  numLeft: float = num
  for unit in ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
    if abs(numLeft) < 1000.0:
      return f"{numLeft:3.0f} {unit}"
    numLeft /= 1000.0
  return f"{numLeft:.1f} YB"


def unindent(source: str) -> str:
  leadingWhitespaces = len(source) - len(source.lstrip())
  if leadingWhitespaces == 0:
    return source
  newLines = [line[leadingWhitespaces:] for line in source.split("\n")]
  return "\n".join(newLines)


def timeago(pastDateMs: int):
  nowMs = time.time() * 1000
  options = [
      {
          "name": "second",
          "divide": 1000
      },
      {
          "name": "minute",
          "divide": 60
      },
      {
          "name": "hour",
          "divide": 60
      },
      {
          "name": "day",
          "divide": 24
      },
      {
          "name": "month",
          "divide": 30.5
      },
  ]
  currentDiff = nowMs - pastDateMs
  if currentDiff < 0:
    raise Exception("The future is NYI")
  resp = "Just now"
  for opt in options:
    currentDiff = round(currentDiff / cast(Union[float, int], opt["divide"]))
    if currentDiff <= 0:
      return resp
    pluralS = ""
    if currentDiff != 1:
      pluralS = "s"
    resp = f"{currentDiff} {opt['name']}{pluralS} ago"
  return resp


def deserializeGzip(contentHash: str, reader: Callable[..., Any]):
  if contentHash not in _deserializeCache:
    _deserializeCache[contentHash] = pickle.loads(gzip.decompress(reader()))
  return _deserializeCache[contentHash]


def serializeBinary(data: bytes) -> Tuple[bytes, str, int]:
  # zstd is not available in snowpark, so move the import here. Can change once we no longer need modelbit in snowpark
  import zstd  # type:ignore
  contentHash = f"sha1:{hashlib.sha1(data).hexdigest()}"
  objSize = len(data)
  compressedPickle = cast(bytes, zstd.compress(data, 10))  # type: ignore
  return (compressedPickle, contentHash, objSize)


def timestamp():
  return int(datetime.timestamp(datetime.now()) * 1000)


def getEnvOrDefault(key: str, defaultVal: str) -> str:
  osVal = os.getenv(key)
  if type(osVal) == str:
    return str(osVal)
  else:
    return defaultVal


def inDeployment() -> bool:
  return 'WORKSPACE_ID' in os.environ


def inRuntimeJob() -> bool:
  return 'JOB_ID' in os.environ


def branchFromEnv() -> str:
  return os.getenv("BRANCH", "main")


def inNotebook() -> bool:
  # From: https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
  # Tested in Jupyter, Hex, DeepNote and Colab
  try:
    import IPython
    return hasattr(IPython.get_ipython(), "config") and len(IPython.get_ipython().config) > 0  #type:ignore
  except (NameError, ModuleNotFoundError):
    return False


def inModelbitCI() -> bool:
  return os.getenv('MODELBIT_CI') == "1"


def inIPythonTerminal() -> bool:
  try:
    import IPython
    return IPython.get_ipython().__class__.__name__ == 'TerminalInteractiveShell'  #type:ignore
  except (NameError, ModuleNotFoundError):
    return False


def getFuncName(func: Callable[..., Any], nameFallback: str) -> str:
  fName = func.__name__
  if fName == "<lambda>":
    gDict = func.__globals__
    for k, v in gDict.items():
      try:
        if v == func:
          return k
      except:
        pass  # DataFrames don't like equality
    return nameFallback
  else:
    return func.__name__


def parseLambdaSource(func: Callable[..., Any]) -> str:
  import inspect
  source = inspect.getsource(func)
  postLambda = source.split("lambda", 1)[-1]
  seenColon = False
  parsedSource = ""
  openParenCount = 0
  i = 0
  while i < len(postLambda):
    cur = postLambda[i]
    if not seenColon:
      if cur == ":":
        seenColon = True
    else:
      if cur == "(" or cur == "[":
        openParenCount += 1
      elif cur == ")" or cur == "]":
        if openParenCount == 0:
          break
        openParenCount -= 1
      elif cur == "," and openParenCount == 0:
        break
      parsedSource += cur
    i += 1
  return parsedSource.strip()


def convertLambdaToDef(lambdaFunc: Callable[..., Any],
                       nameFallback: str = "predict") -> Tuple[Callable[..., Any], str]:
  argNames = list(lambdaFunc.__code__.co_varnames)
  lambdaSource = parseLambdaSource(lambdaFunc)
  funcName = getFuncName(lambdaFunc, nameFallback)
  funcSource = "\n".join([f"def {funcName}({', '.join(argNames)}):", f"  return {lambdaSource}", f""])
  exec(funcSource, lambdaFunc.__globals__, locals())
  return (locals()[funcName], funcSource)


def guessNotebookType() -> Optional[str]:
  try:
    env = os.environ

    def envKeyStartsWith(prefix: str) -> bool:
      for name in env.keys():
        if name.startswith(prefix):
          return True
      return False

    if envKeyStartsWith('HEX_'):
      return 'hex'
    elif envKeyStartsWith('DEEPNOTE_'):
      return 'deepnote'
    elif envKeyStartsWith('VSCODE_'):
      return 'vscode'
    elif envKeyStartsWith('SPY_'):
      return 'spyder'
    elif envKeyStartsWith('JPY_'):
      return 'jupyter'
  except:
    pass
  return None


def guessOs() -> Optional[str]:
  try:
    import psutil
    if psutil.MACOS:
      return "macos"
    if psutil.WINDOWS:
      return "windows"
    if psutil.LINUX:
      return "linux"
  except:
    pass
  return None


def isDsrId(dsName: str) -> bool:
  match = re.match(r'^c[a-z0-9]{24}$', dsName)
  return match is not None


def boto3Client(kind: str):
  import boto3  # type: ignore
  args = dict(modelbitUser=True) if not inRuntimeJob() else dict()
  return boto3.client(kind, **args)
