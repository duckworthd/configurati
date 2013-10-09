import code
import re


def substitute(s):
  """Contents of `...` evaluated in Python"""
  if isinstance(s, basestring) and s.count("`") == 2:
    match = re.search("""^`([^`]+)`$""", s)
    contents, rest = match.group(1), s[match.end():]
    return evaluate(contents)
  else:
    return s


def evaluate(line):
  """Evaluate a line and return its final output"""
  # XXX this isn't smart enough to know about semicolons/newlines in strings,
  # or code where the final result relies on indentation
  line = re.split(";|\n", line)
  line[-1] = "OUTPUT = " + line[-1]
  line = ";".join(line)

  interpreter = code.InteractiveConsole()
  interpreter.push(line)
  return interpreter.locals["OUTPUT"]
