#!/usr/bin/env python
import os
import sys

sys.path.append(os.getcwd())

def ASSERT(cond, errormsg):
    if cond:
        print errormsg
        print "\t\t\tPASS"
    else:
        # COLORS
        print >>sys.stderr, errormsg
        print "\t\t\tFAIL"
        # TODO Add this to something and continue
        # Maybe even raise a token exceptiont o catch so I can
        # examine the stack
        exit()
def START(test):
    # epic kludge
    os.current_test = test
    print("== %s ==" % test)
def END():
    try:
        print("== %s ==" % os.current_test)
    except AttributeError:
        ASSERT(False, "No test in progress")
