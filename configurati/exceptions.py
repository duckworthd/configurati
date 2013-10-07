
class ConfiguratiException(Exception):
  pass


class ValidationError(ConfiguratiException):
  def __init__(self, msg, path=''):
    super(ValidationError, self).__init__("{} ({})".format(msg, path[1:]))
    self.msg  = msg
    self.path = path

  def extend_path(self, path):
    return ValidationError(path=(path + self.path), msg=self.msg)


