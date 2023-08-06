from typing import Callable, Any, cast, Optional, List
import functools, re


class ModelbitJobResult:

  def __init__(
      self,
      func: Callable[..., Any],
      redeploy_on_success: bool = True,
      email_on_failure: Optional[str] = None,
      schedule: Optional[str] = None,
      refresh_datasets: Optional[List[str]] = None,
      size: Optional[str] = None,
      timeout_minutes: Optional[int] = None,
  ):
    if not callable(func):
      raise Exception("Only functions can be decorated as jobs.")
    try:
      self.mb_func = func
      self.mb_obj = self.mb_func()
    except Exception as err:
      if "required positional argument" in str(err):
        raise Exception(
            "Job function arguments require default values. Example: change train(foo) into train(foo = 1).")
      raise err
    if func.__name__ == "source":  # avoid collisions with source.py
      raise Exception("The job function cannot be named 'source'")

    if type(redeploy_on_success) is not bool:
      raise Exception("The redeploy_on_success parameter must be a boolean")
    self.mb_redeployOnSuccess = redeploy_on_success

    if email_on_failure is not None and type(email_on_failure) is not str:
      raise Exception("The email_on_failure parameter must be a string")
    self.mb_emailOnFailure = email_on_failure

    if schedule is not None and type(schedule) is not str:
      raise Exception("The schedule parameter must be a string")
    self.mb_schedule = schedule

    if refresh_datasets is not None and type(refresh_datasets) is not list:
      raise Exception("The refresh_datasets parameter must be a list of strings")
    self.mb_refreshDatasets = refresh_datasets

    if size is not None and size not in ["small", "medium", "large", "xlarge"]:
      raise Exception('The size parameter must be one of "small", "medium", "large", or "xlarge"')
    self.mb_size = size

    if timeout_minutes is not None and (type(timeout_minutes) is not int or timeout_minutes <= 0):
      raise Exception("The timeout_minutes parameter must be a positive integer")
    self.mb_timeoutMinutes = timeout_minutes

  def __getattr__(self, attr: str):
    return getattr(self.mb_obj, attr)

  def __getitem__(self, item: Any):
    return self.mb_obj.__getitem__(item)

  def __str__(self):
    return str(self.mb_obj)

  def __repr__(self):
    return self.__str__()

  def __dir__(self):
    return self.mb_obj.__dir__()


def jobDecorator(
    f: Any = None,
    *,
    redeploy_on_success: bool = True,
    email_on_failure: Optional[str] = None,
    schedule: Optional[str] = None,
    refresh_datasets: Optional[List[str]] = None,
    size: Optional[str] = None,
    timeout_minutes: Optional[int] = None,
):

  if f is None:
    # decorator with parentheses and arguments
    return cast(
        Callable[..., ModelbitJobResult],
        functools.partial(jobDecorator,
                          redeploy_on_success=redeploy_on_success,
                          email_on_failure=email_on_failure,
                          schedule=schedule,
                          refresh_datasets=refresh_datasets,
                          size=size,
                          timeout_minutes=timeout_minutes))

  else:
    # bare decorator, no parentheses or arguments
    @functools.wraps(f)
    def wrapper():
      return ModelbitJobResult(f,
                               redeploy_on_success=redeploy_on_success,
                               email_on_failure=email_on_failure,
                               schedule=schedule,
                               refresh_datasets=refresh_datasets,
                               size=size,
                               timeout_minutes=timeout_minutes)

    return wrapper


def stripJobDecorators(source: str) -> str:
  for decorator in ["@modelbit.job", "@jobDecorator", "@job", "@mb.job"]:
    source = re.sub("(?sm)" + decorator + r".*?def", "def", source, re.M)
  return source
