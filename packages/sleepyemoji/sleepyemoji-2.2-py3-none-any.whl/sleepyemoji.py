#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===================================
# Emoji cli tool
#
#   - Isaac Yep
#===================================
#---README---------------------
# Adding new category:
#   1. add option in main.py (if new category)
#   2. add if case in main.py (if new category)
#   3. add import and if case in toolchain/fetcher.py (if new category)
#   4. add new file in toolchain/ (if new category)
#   5. add emojis to category file in toolchain/
#   6. update usageMessage in toolchain/option_utils.py
# Adding to existing categories:
#   1. Simply append the emoji data in toolchain/<category>.py
#      (copy-paste comment provided for convenience)

mainDocString = '''
This tool prints emojis of one or more catgories, each defined in their own file.
Emojis are given along with their unicode value, discord shorthand, and ios descriptor.

For the official emoji index:
  https://unicode.org/emoji/charts/full-emoji-list.html
'''

#---Dependencies---------------
# stdlib
from sys import argv, exit
# custom modules
from toolchain.fetcher import fetcher
from toolchain.option_utils import usageMessage, checkListOverlap, verifyOption, getOptionVal, stripOptionVals
# 3rd party
try:
  pass
except ModuleNotFoundError:
  print("Error: Missing one or more 3rd-party packages (pip install).")
  exit(1)

# Wrapper
def sleepyemoji(*userArgs):
  userArgs = argv[1:]
  minArgs  = 1
  maxArgs  = 6
  options  = { # ['--takes-arg=', ['int'|'str']]
    'help'     : ['-h', '--help'],
    'complete' : ['-C', '--complete'],
    'animals'  : ['-A', '--animals'],
    'faces'    : ['-F', '--faces'],
    'hands'    : ['-H', '--hands'],
    'icons'    : ['-I', '--icons'],
    'people'   : ['-P', '--people'],
    'combos'   : ['--combos', '--combinations'],
  }
  header_row_width = 60
  emoji_space      = 5
  unicode_space    = 14
  discord_space    = 28
  ios_space        = 20
  combo_space      = 10
  ## Invalid number of args
  if len(userArgs) < (minArgs) or len(userArgs) > (maxArgs):
    usageMessage(f"Invalid number of options in: {userArgs}\nPlease read usage.")
    exit(1)
  ## Invalid option
  if (len(userArgs) != 0) and not (verifyOption(userArgs, options)):
    usageMessage(f"Invalid option(s) entered in: {userArgs}\nPlease read usage.")
    exit(1)
  ## Help option
  if checkListOverlap(userArgs, options['help']):
    print(mainDocString, end='')
    usageMessage()
    exit(0)
  else:
    result = {}
    # complete | -C --complete
    if checkListOverlap(stripOptionVals(userArgs), options['complete']):
      result.update(fetcher('animals','faces','hands','icons','people', 'combos'))
    # animals | -A --animals
    if checkListOverlap(stripOptionVals(userArgs), options['animals']):
      result.update(fetcher('animals'))
    # faces | -F --faces
    if checkListOverlap(stripOptionVals(userArgs), options['faces']):
      result.update(fetcher('faces'))
    # hands | -H --hands
    if checkListOverlap(stripOptionVals(userArgs), options['hands']):
      result.update(fetcher('hands'))
    # icons | -I --icons
    if checkListOverlap(stripOptionVals(userArgs), options['icons']):
      result.update(fetcher('icons'))
    # people | -P --people
    if checkListOverlap(stripOptionVals(userArgs), options['people']):
      result.update(fetcher('people'))
    # combos | --combos --combinations
    if checkListOverlap(stripOptionVals(userArgs), options['combos']):
      result.update(fetcher('combos'))

    if len(result.keys()) == 0:
      print(f"Request was valid, however there are no entries.")
      exit(0)
    else:
      print('─'*header_row_width)
      print(f"Emoji │ Value{' '*(unicode_space - len('Value'))}Discord{' '*(discord_space - len('Discord'))}ios{' '*(ios_space - len('ios'))}")
      print('─'*header_row_width)
      for i in result.keys():
        emoji   = i
        val     = f"{emoji!a}".lstrip("'").rstrip("'")
        discord = result[i][0]
        ios     = result[i][1]

        if (not discord) and (not result) :
          print(f"{emoji}{' '*(combo_space - len(emoji))}(combo)")
        else:
          print(f"{emoji:<{emoji_space}}│ ", end='')
          print(f"{val:<{unicode_space}}", end='')
          print(f"{discord:<{discord_space}}", end='')
          print(f"{ios:<{ios_space}}", end='\n')
      exit(0)
