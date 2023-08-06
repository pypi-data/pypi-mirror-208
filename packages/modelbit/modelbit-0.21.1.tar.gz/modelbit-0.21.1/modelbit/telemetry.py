import logging
import os
import sys
import traceback
from typing import Optional

from modelbit.api import MbApi
from modelbit.error import ModelbitException, UserFacingException

from .ux import printTemplate

logger = logging.getLogger(__name__)


def initLogging():
  LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
  logging.basicConfig(level=LOGLEVEL)


def _logErrorToWeb(mbApi: Optional[MbApi], userErrorMsg: str):
  from modelbit.api import MbApi
  mbApi = mbApi or MbApi()
  errStack = traceback.format_exception(*sys.exc_info())[1:]
  errStack.reverse()
  errorMsg = userErrorMsg + "\n" + "".join(errStack)
  try:
    mbApi.getJson("api/cli/v1/error", {"errorMsg": errorMsg})
  except Exception as e:
    logger.info(e)


def eatErrorAndLog(mbApi: Optional[MbApi], genericMsg: str):

  def decorator(func):

    def innerFn(*args, **kwargs):
      error = None  # Stored error so stack trace doesn't contain our internals.
      try:
        return func(*args, **kwargs)
      except UserFacingException as e:
        if e.logToModelbit:
          _logErrorToWeb(mbApi, e.userFacingErrorMessage)
        printTemplate("error", None, errorText=genericMsg + " " + e.userFacingErrorMessage)
        error = e.userFacingErrorMessage
      except Exception as e:
        specificError = getattr(e, "userFacingErrorMessage", None)
        errorMsg = genericMsg + (" " + specificError if specificError is not None else "")
        _logErrorToWeb(mbApi, errorMsg)
        printTemplate("error_details", None, errorText=errorMsg, errorDetails=traceback.format_exc())
        error = errorMsg
      # Convert to generic ModelbitException.
      if error is not None:
        raise ModelbitException(error)

    return innerFn

  return decorator
