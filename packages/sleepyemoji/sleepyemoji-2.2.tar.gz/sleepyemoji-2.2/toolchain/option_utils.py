# Utility: Usage Message
def usageMessage(errorNotice: str = '') -> str:
  if errorNotice:
    errorNotice += '\n\n'
  print(f"""
{errorNotice}
Provide 1 or more options of various emoji categories, or simply request all of them.
--------------
All:
  ./main.py [-C|--complete]
Categories:
  /main.py [*flags]
    [-A|--animals]
    [-F|--faces]
    [-H|--hands]
    [-I|--icons]
    [-P|--people]
    [--combos|--combinations]
Example:
  ./main.py -A -H
Info:
  ./main.py [-h|--help]
--------------
""")

# Utility: Verify against all options
def verifyOption(args: list, options: dict) -> bool:
  res = []
  for arg in args:
    flag = False
    if '=' in arg:
      pretext = arg[:arg.index('=')+1]
      val = arg[arg.index('=')+1:]
      for optionTypeName in options.keys():
        if options[optionTypeName][0] == pretext:
          if (options[optionTypeName][1] == 'int') and val.isdigit():
            flag = True
          elif (options[optionTypeName][1] == 'str') and (not val.isdigit()):
            flag = True
    else:
      for optionTypeName in options.keys():
        for opFlag in options[optionTypeName]:
          if arg == opFlag:
            flag = True
    res.append(flag)
  return (False not in res)

# Utility: Check list overlap
def checkListOverlap(l1: list, l2: list) -> bool:
  return [i for i in l1 if i in l2] != []

# Utility : Get value from option input
def getOptionVal(args: list, key:list):
  for arg in args:
    if key[0] in arg:
      val = arg[arg.index('=')+1:]
      if val.isdigit():
        return int(val)
      return val

# Utility : Strip values from args
def stripOptionVals(args: list) -> list:
  res = []
  for arg in args:
    if '=' in arg:
      res.append(arg[:arg.index('=')+1])
    else:
      res.append(arg)
  return res