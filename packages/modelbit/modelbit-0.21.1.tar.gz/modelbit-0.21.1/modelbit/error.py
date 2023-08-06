class UserFacingException(Exception):
  userFacingErrorMessage: str
  logToModelbit: bool

  def __init__(self, message: str, logToModelbit: bool = True) -> None:
    self.userFacingErrorMessage = message
    self.logToModelbit = logToModelbit
    super().__init__(message)


class ModelbitException(Exception):
  pass
