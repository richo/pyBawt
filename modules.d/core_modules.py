import re
import time
import ourgit
import os
import sys
import atexit
import traceback
from lib import *
import logging

VERSION="$Rev: 1252 $".split(" ")[1]

class ModuleAlreadyLoaded(Exception):
    pass

# TODO Split this out into core modules, and then import a set of user added
# ones. BawtModule and the stuff to do reloads is all that needs to be global
# TODO Work out how the channel infrastructure will work (structured
# import?)(Circular ref??)
# Implement something to reference these by name instead of type hax.
class WriteThing(object):
    def __init__(self, writable, target):
        self.w = writable
        self.target = target
    def write(self, msg):
        self.w.privmsg(self.target, msg)


class HelpModule(BawtM2):
    """Allows for reading the docstring of arbitrary modules"""
    _name = "HelpModule"
    privmsg_re = "^(!|%(nick)s:\s+)(help) ?([^ ]*)"
    def handle_privmsg(self, msg):
        if self.m.group(3):
            for i in get_help(self.m.group(3)).split("\n"):
                self.parent.privmsg(msg.replyto, "%s: %s" % (msg.nick, i))
        else:
            self.parent.privmsg(msg.replyto, "%s: help [module]" % (msg.nick))
class SourceModule(BawtM2):
    """Contains the commands for interacting with pyBawts internal source management and update routines"""
    _commands = ['reload', 'update', 'version']
    privmsg_re = "^(!|%(nick)s:\s?)(%(commands)s)" % {'commands': "|".join(_commands),
            'nick': '%(nick)s'}
    _name = "SourceModule" 
    def handle_privmsg(self, msg):
        if not self.auth(msg):
            self.parent.privmsg(msg.replyto, "%s: I don't know you." % (msg.nick))
            return
        argv = msg.data_segment.split(" ")
        if self.m.group(2) == "reload":
            status = self.parent.reload_modules()
            if status:
                self.parent.privmsg(msg.replyto, "%s: Reload Complete." % (msg.nick))
            else:
                t = WriteThing(self.parent, msg.nick)
                self.parent.privmsg(msg.replyto, "%s: Reload Failed! (pm for stackdump)" % (msg.nick))
                # TODO- this isn't actually the error in question. Lol.
                #traceback.print_tb(status, file=t)
                traceback.print_exception(*status.args, file=t)
        elif self.m.group(2) == "update":
            self.parent.privmsg(msg.replyto, ourgit.update_git())
        elif self.m.group(2) == "version":
            self.parent.privmsg(msg.replyto, "%(nick)s: %(version)s on %(branch)s" %
                    {   "nick": msg.nick,
                        "version": ourgit.version(),
                        "branch": ourgit.current_branch()})
        elif self.m.group(2) == "checkout":
            self.parent.privmsg(msg.replyto, "Not implemented LOL!")

class AdminModule(BawtM2):
    """Houses nearly everything that needs Authentication"""
    _commands = ['loaded', 'restart', 'del', 'modlist']
    privmsg_re = "^(!|%(nick)s:\s?)(%(commands)s) ?" % {'commands': "|".join(_commands),
            'nick': '%(nick)s'}
    _name = "AdminModule" 
    def handle_privmsg(self, msg):
        if not self.auth(msg):
            self.parent.privmsg(msg.replyto, "%s: I don't know you." % (msg.nick))
            return
        argv = msg.data_segment.split(" ")
        # TODO - Second argument for channel.
        # TODO - Hax at this to replace the argv[0] matching based on a regex group to pull the commnad

        if self.m.group(2) == "loaded":
            self.parent.privmsg(msg.replyto, self.channel.dump_modules())
        elif self.m.group(2) == "del":
            self.parent.privmsg(msg.replyto, "Sorry, not implemented")
        elif self.m.group(2) == "restart":
            raise Restart
        elif self.m.group(2) == "modlist":
            self.parent.privmsg(msg.replyto, "%(nick)s: %(mods)s" % {'nick': msg.nick,
                'mods': ', '.join(self.parent.available_modules())})
        else:
            self.parent.privmsg(msg.replyto, "I have NFI how you managed this.")

class DebugModule(BawtM2):
    """Houses nearly everything that needs Authentication"""
    _commands = ['version', 'nick', 'uname', 'dumpchans', 'argv' ]
    privmsg_re = "^!(%(commands)s)" % {'commands': "|".join(_commands)}
    _name = "DebugModule"
    def handle_privmsg(self, msg):
        if not self.auth(msg):
            self.parent.privmsg(msg.replyto, "%s: I don't know you." % (msg.nick))
            return
        argv = msg.data_segment.split(" ")
        # TODO - Second argument for channel.
        if argv[0] == "!version":
            self.parent.privmsg(msg.replyto, "Modules: %(modv)s, Global: %(gvs)s" % {
                        'modv': VERSION,
                        'gvs': ourgit.version()
                        })
        elif argv[0] == "!nick":
            self.parent.privmsg(msg.replyto, "%s: As far as I know, my nick is %s" % (msg.nick, self.parent.nick))
        elif argv[0] == "!uname":
            self.parent.privmsg(msg.replyto, " ".join(os.uname()))
        elif argv[0] == "!dumpchans":
            for i in self.parent.dump_channel_data():
                self.parent.privmsg(msg.replyto, i)
        elif argv[0] == "!argv":
            self.parent.privmsg(msg.replyto, str(sys.argv))
        else:
            self.parent.privmsg(msg.replyto, "I have NFI how you managed this.")

class AddModule(BawtM2):
    privmsg_re = "^(!|%(nick)s:\s?)(add) ([^ ]*)"
    _name = "AddModule"
    def handle_privmsg(self, msg):
        if not self.auth(msg):
            self.parent.privmsg(msg.replyto, "%s: I don't know you." % (msg.nick))
            return
        mod = self.m.group(3)
        try:
            if self.parent.add_module(msg.origin.lower(), mod):
                logging.info("%s loaded module %s in %s" % (msg.nick, mod, msg.origin.lower()))
                self.parent.privmsg(msg.replyto, "done.")
            else:
                self.parent.privmsg(msg.replyto, "No such module")
        except ModuleAlreadyLoaded:
                logging.info("%s attempted to load duplicate module %s in %s" % (msg.nick, mod, msg.origin.lower()))
                self.parent.privmsg(msg.replyto, "Module already loaded in this context")
        except IndexError:
            self.parent.privmsg(msg.replyto, "Module?")

class ChanModule(BawtM2):
    _commands = ['join', 'part', 'kick']
    privmsg_re = "^!(%(commands)s)" % {'commands': "|".join(_commands)}
    _name = "ChanModule"
    def handle_privmsg(self, msg):
        if not self.auth(msg):
            logging.info("%s attempted to %s without auth" % (msg.nick, msg.data_segment))
            self.parent.privmsg(msg.replyto, "%s: I don't know you." % (msg.nick))
            return
        argv = msg.data_segment.split(" ")
        if argv[0] == '!join':
            if len(argv) == 1:
                self.parent.privmsg(msg.replyto, "%s: Join which channel?" % (msg.nick))
                return
            self.parent.join(argv[1])
        elif argv[0] == '!part':
            if len(argv) == 1:
                self.parent.part(msg.replyto)
            else:
                self.parent.part(argv[1])
        elif argv[0] == '!kick':
            if len(argv) == 1:
                self.parent.privmsg(msg.replyto, "%s: Kick whom?" % (msg.nick))
                return
            self.parent.kick(msg.replyto, argv[1], "Zot! Kicked")


class DumpModule(BawtM2):
    _name = "DumpModule"
    def handle_privmsg(self, msg):
        msg.dump()
    def handle_notice(self, msg):
        msg.dump()

class ChannelMapping(Mapping):
    def refcount(self, nick, insensitive=True):
        count = 0
        if insensitive:
            nick = nick.lower()
        for i in self.itervalues():
            # Not actually respecting insensitiv
            if nick in map(lambda n: n.lower, i):
                count += 1
        return count

class AuthModule(BawtM2):
    _name = "AuthModule"
    _commands = ['auth', 'status']
    privmsg_re = "^!(%(commands)s)" % {'commands': "|".join(_commands)}
    visible = ChannelMapping()
    def handle_privmsg(self, msg):
        # TODO Global is_private
        argv = msg.data_segment.split(" ")
        if argv[0] == "!auth":
            if len(argv) == 1 or not msg.is_private():
                self.parent.privmsg(msg.replyto,
                        "%s: Usage /msg %s !auth [password]" %
                        (msg.nick, self.parent.nick))
                return
            if self.parent.authenticator.try_auth(msg, argv[1]):
                logging.info("%s authenticated successfully" % msg.nick)
                self.parent.privmsg(msg.replyto, "This has been a triumph")
            else:
                logging.info("%s has failed to authenticated" % msg.nick)
                self.parent.privmsg(msg.replyto, "You have chosen poorly")
            return
        elif argv[0] == "!status":
            if self.auth(msg.nick):
                self.parent.privmsg(msg.replyto, "You are identified")
            else:
                self.parent.privmsg(msg.replyto, "You are not identified")
    def handle_nick(self, msg):
        self.handle_part(msg)
    def handle_join(self, msg):
        logging.info("Sighting %s" % msg.nick)
        self.visible[msg.address_segment].append(msg.nick)
    def handle_part(self, msg):
        logging.info("Losing sight of %s" % msg.nick)
        try:
            self.visible[msg.address_segment].remove(msg.nick)
        except ValueError:
            logging.fixme("%s left %s without having been seen, testing auth anyway" % (msg.nick, msg.address_segment))
        if self.visible.refcount(msg.nick) == 0:
            logging.info("Can't see %s; deauthing" % msg.nick)
            self.parent.authenticator.revoke_auth(msg.nick)
