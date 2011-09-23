#!/usr/bin/python
"""A module wrapper around the config files for pyBawt"""
__all__ = []

# This is tremendous hax, just a piece of scaffold to avoid breaking the old
# API
# Also, bail the fuck out if the config is incomplete

import logging
import os

class InvalidConfig(Exception):
    pass
class NoConfigFile(Exception):
    pass


CONFIG_FILE = 'pyBawt.conf'
logging.info("Commencing config read from %s" % (os.path.join(os.getcwd(), CONFIG_FILE)))
config = {}
boolvalues = { 'true' : True,
               '1'    : True,
               'yes'  : True,
               'false': False,
               '0'    : False,
               'no'   : False }
def to_bool(val):
    return boolvalues[val.lower()]
def to_list(val):
    return list(map(lambda x: x.strip(), val.split(',')))
def passthru(val):
    return val
# A tuple of tuples with a key and an transformer
keys = (('host', passthru),
        ('ssl' , to_bool),
        ('nick', passthru),
        ('port', int),
        ('auth_host', passthru),
        ('auth_hash', passthru),
        ('channels' , to_list),
        ('nickserv_nick', passthru),
        ('nickserv_pass', passthru)
       )

with open(CONFIG_FILE) as fh:
    for line in fh:
        line = line.strip()
        if line.startswith("#"):
            # Ignore comments
            continue
        if not line:
            continue
        try:
            key, value = map(lambda x: x.strip(),line.split('=', 1))
            config[key] = value
        except ValueError:
            raise InvalidConfig, "Invalid key value pair at (FIXME Lineno)"
if not config:
    logging.error("Couldn't open config file")
    raise NoConfigFile
    # FIXME distinguish between not there and inaccessible
for name, transformer in keys:
    __all__.append(name)
    try:
        # This is fucked XXX FIXME
        #__dict__[name] = transformer(config[name])
        exec('%s = %s' % (name, repr(transformer(config[name]))))

    except ValueError: #Probably port didn't translate
        raise InvalidConfig
