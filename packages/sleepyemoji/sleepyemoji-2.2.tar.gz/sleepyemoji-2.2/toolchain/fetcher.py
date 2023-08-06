#---Dependencies---------------
from toolchain.animals import animalsDict
from toolchain.faces import facesDict
from toolchain.hands import handsDict
from toolchain.icons import iconsDict
from toolchain.people import peopleDict
from toolchain.combos import combosDict



# Utility : Fetches
def fetcher(*args) -> dict:
  args = list(args)
  payload = {}
  if 'animals' in args:
    payload.update(animalsDict)
  if 'faces' in args:
    payload.update(facesDict)
  if 'hands' in  args:
    payload.update(handsDict)
  if 'icons' in args:
    payload.update(iconsDict)
  if 'people' in args:
    payload.update(peopleDict)
  if 'combos' in args:
    payload.update(combosDict)
  
  if len(payload.keys()) == 0:
    print(f"Request was valid, however there are no entries.")
    return {}
  else:
    return payload