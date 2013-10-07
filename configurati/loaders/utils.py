import code
import re


def substitute(s):
  """Contents of `...` evaluated in Python"""
  if isinstance(s, basestring) and s.count("`") == 2:
    match = re.search("""`([^`]+)`""", s)
    contents, rest = match.group(1), s[match.end():]
    return str(evaluate(contents)) + rest
  else:
    return s


def evaluate(line):
  """Evaluate a line and return its final output"""
  line = line.split(";")
  line[-1] = "OUTPUT = " + line[-1]
  line = ";".join(line)

  interpreter = code.InteractiveConsole()
  interpreter.push(line)
  return interpreter.locals["OUTPUT"]
