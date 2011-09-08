#!/usr/bin/env python

##
# Insert License
##

# Rich Healey '08

import ircSocket
import time
import sys
import os
import random
import config
import bModules
import logging

logging.info("pyBawt started")

# Have a crack at sweet argparsing

# TODO - hax involving stdout for debugging

try:
    import argparse
    parser = argparse.ArgumentParser(description='IRC bot written in python')
    parser.add_argument("-d", "--debug", dest='debug', action='store_true',
            default=False,
            help='include debug data, also crash violently on error')
    args = parser.parse_args()

    debug = args.debug
except ImportError:
# no argparse, probably py2.6
    debug = False
    # TODO - something clever here to make args still work

def restart_stub():
    net.quit("Going down for restart")
    os.execv(sys.executable, [sys.executable] + sys.argv)

net = ircSocket.chatnet(config.host, port=config.port, use_ssl=config.ssl)
# Ugly hax, port to argparse if we see any more nicks
nick = config.nick
net.identify(nick)
net.auth_self('nickserv', 'b@dpass')
net._debug = True

# Before we hit mainloop, write pidfile
try:
    fh = open('/tmp/pyBawt.pid', 'w')
    fh.write(str(os.getpid()))
    fh.close()
except IOError:
    print "Couldn't write pidfile"
    exit()

try:
    for i in config.channels:
        net.join(i)
    while True:
        try:
            net.recv_wait()
        except ircSocket.FlushQueue:
            pass
        net.dump_queue()
except KeyboardInterrupt:
    logging.error("Shutting down due to user intervention")
    net.quit("Killed from terminal")
except bModules.Restart:
    # TODO Include the user who did this
    logging.error("Restarting due to user intervention")
    restart_stub()
except ircSocket.IrcDisconnected:
    if ircSocket.should_reconnect():
        restart_stub()
except ircSocket.IrcTerminated:
    # Catch but don't handle, die gracefully
    pass
except Exception:
    # TODO - Checkout from stable git branch
    if debug: # Debug hook? Either way it's stupid.
        logging.error("Shutting down and bailing out")
        raise
    else:
        logging.error("Exception caught, restarting")
        traceback.print_exception(*sys.exc_info(), file=logging.Writer(logging.error))
        restart_stub()

