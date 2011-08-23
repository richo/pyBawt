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
import channels
import networks
import bModules
import logging

logging.info("pyBawt started at %s" % time.asctime())

# Have a crack at sweet argparsing

# TODO - hax involving stdout for debugging

try:
    import argparse

    # TODO Validate the host option agains networks.networks.key()
    parser = argparse.ArgumentParser(description='IRC bot written in python')
    parser.add_argument('host', nargs='?', default=networks.default,
            help="IRC host to connect to, defaults to %(host)s" % {"host": networks.default})
    parser.add_argument("-n", "--nick", dest='nick', action='store',
            default='pyBawt',
            help='define nick to use')
    parser.add_argument("-d", "--debug", dest='debug', action='store_true',
            default=False,
            help='include debug data, also crash violently on error')
    args = parser.parse_args()

    network = networks.networks[args.host]
    nick = args.nick
    debug = args.debug
except ImportError:
# no argparse, probably py2.6
    if len(sys.argv) < 2:
        network = networks.networks[networks.default]
    else:
        network = networks.networks[sys.argv[1]]
    debug = False
    # TODO - something clever here to make args still work

def restart_stub():
    net.quit("Going down for restart")
    os.execv(sys.executable, [sys.executable] + sys.argv)

net = ircSocket.chatnet(network.host, port=network.port, use_ssl=network.ssl)
# Ugly hax, port to argparse if we see any more nicks
nick = network.nick
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
    for i in channels.channels[network.host]:
        net.join(i)
    while True:
        try:
            net.recv_wait()
        except ircSocket.FlushQueue:
            pass
        net.dump_queue()
except KeyboardInterrupt:
    logging.error("Shutting down at %s due to user intervention" % time.asctime())
    net.quit("Killed from terminal")
except bModules.Restart:
    # TODO Include the user who did this
    logging.error("Restarting at %s due to user intervention" % time.asctime())
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
        logging.error("Restarting at %s bailing out" % time.asctime())
        raise
    else:
        logging.error("Restarting at %s, restarting" % time.asctime())
        restart_stub()

