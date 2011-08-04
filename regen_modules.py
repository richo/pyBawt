#!/usr/bin/python
MODULE_DIRECTORY = 'modules.d'
CONFIG = 'module_config.py'
outfile = 'bModules.py'

import os

def rebuild_bModules():
    out = open(outfile, 'w')
    # Module directory
    modules = []
    for i in os.listdir(MODULE_DIRECTORY):
        modules.append(os.path.join(MODULE_DIRECTORY, i))
    modules.sort()
    modules.append(CONFIG)
    for i in modules:
        if not i.endswith(".py"):
            continue
        if os.path.isdir(i):
            continue
        # We're happy with the file.
        for line in open(i, 'r').readlines():
            out.write(line)
    out.close()
    return outfile

def save_modules(module_map):
    pass
# XXX TODO construct this function to save to module_config.py

if __name__ == '__main__':
    # Test rig
    rebuild_bModules()



