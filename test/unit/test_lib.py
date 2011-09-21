#!/usr/bin/env python
from helpers import *

import lib

START("LowerList")
# LowerList should behave like a list
lowerlist = lib.LowerList()
lowerlist.append("UpPeR CaSe")

# LowerList should be case insensitive
ASSERT("upper case" in lowerlist, "LowerList should be case insensitive")
END()

START("Mapping")
mapping = lib.Mapping()
mapping["rawr"] = "Thing"

ASSERT("rawr" in mapping, "Regular assignment works")

mapping["doesntexist"].append("rawr")

ASSERT("rawr" in mapping["doesntexist"], "Creating keys by referencing them")
END()
