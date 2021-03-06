#!/usr/bin/python
MODULE_DIRECTORY = 'modules.d'
LOCAL_MODULES = 'modules.local.d'
CONFIG = 'module_config.py'
outfile = 'bModules.py'

import os

def rebuild_bModules():
    out = open(outfile, 'w')
    # Module directory
    modules = [os.path.join(MODULE_DIRECTORY, i) for i in os.listdir(MODULE_DIRECTORY)]
    if os.path.exists(LOCAL_MODULES):
        modules.append(os.path.join(LOCAL_MODULES, i) for i in os.listdir(LOCAL_MODULES)
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



