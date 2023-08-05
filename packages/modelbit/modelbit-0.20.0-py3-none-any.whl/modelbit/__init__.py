__version__ = "0.20.0"
__author__ = 'Modelbit'

import os, sys, yaml, pickle, logging
from types import ModuleType
from typing import cast, Union, Callable, Any, Dict, List, Optional, TYPE_CHECKING

# aliasing since some of these overlap with functions we want to expose to users

from . import warehouses as m_warehouses
from . import deployments as m_deployments
from . import runtime as m_runtime
from . import utils as m_utils
from . import helpers as m_helpers
from . import model_wrappers as m_model_wrappers
from . import collect_dependencies as m_collect_dependencies
from . import email as m_email
from . import jobs as m_jobs
from . import telemetry as m_telemetry
from . import secrets as m_secrets

if TYPE_CHECKING:
  import pandas
  import modelbit.internal.datasets as m_datasets

m_helpers.pkgVersion = __version__

m_telemetry.initLogging()
logger = logging.getLogger(__name__)


# Nicer UX for customers: from modelbit import Deployment
class Deployment(m_runtime.Deployment):
  ...


def job(
    f: Any = None,
    *,
    redeploy_on_success: bool = True,
    email_on_failure: Optional[str] = None,
    schedule: Optional[str] = None,
    refresh_datasets: Optional[List[str]] = None,
    size: Optional[str] = None,
    timeout_minutes: Optional[int] = None,
):
  "Decorator to save a function as a job."
  return m_jobs.jobDecorator(f=f,
                             redeploy_on_success=redeploy_on_success,
                             email_on_failure=email_on_failure,
                             schedule=schedule,
                             refresh_datasets=refresh_datasets,
                             size=size,
                             timeout_minutes=timeout_minutes)


def __str__():
  return "Modelbit Client"


def _repr_html_():  # type: ignore
  return __str__()


def datasets() -> 'm_datasets.DatasetList':
  import modelbit.internal.datasets as m_datasets
  return m_datasets.list()


def get_dataset(dsName: str,
                filters: Optional[Dict[str, List[Any]]] = None,
                filter_column: Optional[str] = None,
                filter_values: Optional[List[Any]] = None,
                optimize: bool = True) -> Optional['pandas.DataFrame']:
  import modelbit.internal.datasets as m_datasets
  return m_datasets.get(dsName, filters, filter_column, filter_values, optimize)


def warehouses() -> 'm_warehouses.WarehousesList':
  return m_warehouses.list()


def deployments() -> 'm_deployments.DeploymentsList':
  return m_deployments.list()


def add_files(deployment: str,
              files: Union[List[str], Dict[str, str]],
              modelbit_file_prefix: Optional[str] = None,
              strip_input_path: Optional[bool] = False):
  return m_runtime.add_files(deployment, files, modelbit_file_prefix, strip_input_path)


def add_objects(deployment: str, values: Dict[str, Any]):
  return m_runtime.add_objects(deployment, values)


def get_secret(name: str,
               deployment: Optional[str] = None,
               branch: Optional[str] = None,
               encoding: str = "utf8") -> str:
  return m_secrets.get_secret(name, deployment, branch, encoding)


def add_package(path: str, force: bool = False):
  from .package import auth_and_add_package
  return auth_and_add_package(path, force)


def add_module(m: ModuleType):
  from .package import auth_and_add_module
  return auth_and_add_module(m)


def delete_package(name: str, version: str):
  from .package import auth_and_delete_package
  return auth_and_delete_package(name, version)


def deploy(deployableObj: Union[Callable[..., Any], 'm_runtime.Deployment'],
           name: Optional[str] = None,
           python_version: Optional[str] = None,
           python_packages: Optional[List[str]] = None,
           system_packages: Optional[List[str]] = None,
           dataframe_mode: bool = False,
           example_dataframe: Optional['pandas.DataFrame'] = None):
  m_helpers.refreshAuthentication()  # Refreshes default environment
  if _objIsDeployment(deployableObj):
    deployableObj = cast(Deployment, deployableObj)
    return deployableObj.deploy()
  elif callable(deployableObj) and deployableObj.__name__ == "<lambda>":
    return m_model_wrappers.LambdaWrapper(deployableObj,
                                          name=name,
                                          python_version=python_version,
                                          python_packages=python_packages,
                                          system_packages=system_packages,
                                          dataframe_mode=dataframe_mode,
                                          example_dataframe=example_dataframe).makeDeployment().deploy()
  elif callable(deployableObj):
    return Deployment(name=name,
                      deploy_function=deployableObj,
                      python_version=python_version,
                      python_packages=python_packages,
                      system_packages=system_packages,
                      dataframe_mode=dataframe_mode,
                      example_dataframe=example_dataframe).deploy()
  elif hasattr(deployableObj, "__module__") and "sklearn" in deployableObj.__module__ and hasattr(
      deployableObj, "predict"):
    return m_model_wrappers.SklearnPredictor(deployableObj,
                                             name=name,
                                             python_version=python_version,
                                             python_packages=python_packages,
                                             system_packages=system_packages,
                                             dataframe_mode=dataframe_mode,
                                             example_dataframe=example_dataframe).makeDeployment().deploy()
  else:
    raise Exception("First argument must be a function or Deployment object.")


def login(region: Optional[str] = None):
  m_helpers.performLogin(refreshAuth=True, region=region)
  return sys.modules['modelbit']


def switch_branch(branch: str):
  m_helpers.setCurrentBranch(branch)


def isAuthenticated() -> bool:
  return m_helpers.isAuthenticated()


def load_value(name: str, restoreClass: Optional[type] = None):
  if name.endswith(".pkl"):
    import __main__ as main_package
    # Support finding files relative to source location
    # This doesn't work from lambda, so only use when not in a deployment
    if not os.path.exists(name):
      name = os.path.join(os.path.dirname(main_package.__file__), name)

    with open(name, "rb") as f:
      value = pickle.load(f)
      if restoreClass is not None and isinstance(value, m_helpers.InstancePickleWrapper):
        return value.restore(restoreClass)
      else:
        return value
  extractPath = os.environ['MB_EXTRACT_PATH']
  objPath = os.environ['MB_RUNTIME_OBJ_DIR']
  if not extractPath or not objPath:
    raise Exception("Missing extractPath/objPath")
  with open(f"{extractPath}/metadata.yaml", "r") as f:
    yamlData = cast(Dict[str, Any], yaml.load(f, Loader=yaml.SafeLoader))  # type: ignore
  data: Dict[str, Dict[str, str]] = yamlData["data"]
  contentHash = data[name]["contentHash"]
  with open(f"{objPath}/{contentHash}.pkl.gz", "rb") as f:
    return m_utils.deserializeGzip(contentHash, f.read)


def save_value(obj: Any, filepath: str):
  if not m_collect_dependencies.savedSpecialObj(obj, filepath):
    with open(filepath, "wb") as f:
      pickle.dump(obj, f)


def send_email(subject: str, to: List[str], msg: str):
  m_email.sendEmail(subject=subject, to=to, msg=msg)


def _objIsDeployment(obj: Any):
  try:
    if type(obj) in [Deployment, m_runtime.Deployment]:
      return True
    # catch modelbit._reload() class differences
    if obj.__class__.__name__ in ['Deployment']:
      return True
  except:
    return False
  return False


def parseArg(s: str) -> Any:
  import json
  try:
    return json.loads(s)
  except json.decoder.JSONDecodeError:
    return s
