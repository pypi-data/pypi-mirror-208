#!/usr/bin/env python3

from typing import Optional
import logging
import time


def retry(retries: int, logger: Optional[logging.Logger]):

  def decorator(func):

    def innerFn(*args, **kwargs):
      lastError: Optional[Exception] = None
      for attempt in range(retries):
        try:
          return func(*args, **kwargs)
        except Exception as e:
          lastError = e
          retryTime = 2**attempt
          if logger and attempt > 2:
            logger.warn("Retrying in %ds.", retryTime)
          time.sleep(retryTime)
      if lastError is None:
        raise Exception(f"Failed after {retries} retries. Please contact support.")
      raise lastError

    return innerFn

  return decorator
