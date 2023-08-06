import logging
import os
import sys
import traceback

from .helpers import getJson, isAuthenticated
from .ux import printTemplate

logger = logging.getLogger(__name__)


def initLogging():
  LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
  logging.basicConfig(level=LOGLEVEL)


def _logErrorToWeb(userErrorMsg: str):
  errStack = traceback.format_exception(*sys.exc_info())[1:]
  errStack.reverse()
  errorMsg = userErrorMsg + "\n" + "".join(errStack)
  try:
    getJson("jupyter/v1/error", {"errorMsg": errorMsg})
  except Exception as e:
    logger.info(e)


def eatErrorAndLog(genericMsg: str):

  def decorator(func):

    def innerFn(*args, **kwargs):
      try:
        return func(*args, **kwargs)
      except UserFacingException as e:
        if e.logToModelbit and isAuthenticated():
          _logErrorToWeb(e.userFacingErrorMessage)
        printTemplate("error", None, errorText=e.userFacingErrorMessage)
      except Exception as e:
        errorMsg = getattr(e, "userFacingErrorMessage", genericMsg)
        if isAuthenticated():
          _logErrorToWeb(errorMsg)
        printTemplate("error_details", None, errorText=errorMsg, errorDetails=traceback.format_exc())

    return innerFn

  return decorator


class UserFacingException(Exception):
  userFacingErrorMessage: str
  logToModelbit: bool

  def __init__(self, message: str, logToModelbit: bool = True) -> None:
    self.userFacingErrorMessage = message
    self.logToModelbit = logToModelbit
    super().__init__(message)
