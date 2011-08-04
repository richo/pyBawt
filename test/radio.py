#!/usr/bin/env python

import sys
sys.path.append("../")
import mpd

c = mpd.MPDClient()
c.connect("domino.psych0tik.net", 6600)
print c.currentsong()

