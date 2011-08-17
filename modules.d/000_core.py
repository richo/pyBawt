"""This module represents the core features a developer needs to write modules
for the pyBawt framework"""
import re
import time
import ourgit
import os
import sys
import atexit

VERSION="$Rev: 1252 $".split(" ")[1]

def get_help(mdl):
    try:
        obj = globals()[mdl]
    except KeyError:
        return "No help for %s" % mdl
    if hasattr(obj, '_commands'):
        return ", ".join(obj._commands) + "\n" + str(obj.__doc__)
    else:
        return str(obj.__doc__)

# CORE
#-----

class Restart(Exception):
    pass
class StopHandling(Exception):
    pass

class BawtModule(object):
    """This is a hax module, it just says hi to people"""
    matcher_re = "hi %(nick)s"
    matcher_flags = 0
    _name = "BawtModule"
    def __init__(self, parent, channel):
        self.parent = parent
        self.channel = channel
        self.rehash()
    def __repr__(self):
        return self._name
    def __str__(self):
        return self._name
    def rehash(self):
        """Reconstruct matcher regex"""
        self.matcher = re.compile(self.matcher_re % {'nick': self.parent.nick}, # ADD more as neededh
                                  self.matcher_flags)
    def want(self, msg):
        # OLD API, compat
        return self.matcher.search(msg.data_segment)

    def handle(self, msg):
        self.parent.privmsg(msg.replyto, "%s: Hi!" % (msg.nick))

class BawtM2(object):
    """I'm a lazy programmer who doesn't write help files"""

# Match everything by default
    privmsg_re = "."
    privmsg_flags = 0
    topic_re = "."
    topic_flags = 0
    mode_re = "."
    mode_flags = 0
    join_re = "."
    join_flags = 0
    kick_re = "."
    kick_flags = 0
    part_re = "."
    part_flags = 0
    notice_re = "."
    notice_flags = 0
    # For !list
    _name = "BawtM2"
    # for is_action
    action_matcher = re.compile("^\x01ACTION.*\x01$")
    def __init__(self, parent, channel):
        self.parent = parent
        self.channel = channel
        self.re_data = {'nick': self.parent.nick}# ADD more as neededh
        self.rehash()

        # Default authentication method is a match of the hostmask against the
        # Message. I fully expect this to be overridden.

        # Or against a static hash
        self.auth = self.parent.Authenticator.authed
        self.on_load()

    def __repr__(self):
        return self._name
    def __str__(self):
        return self._name
    def require(self, prop):
        # TODO - Flesh these out
        """XXX Unratified API"""
        return self.__getattr__("_require_%s" % prop)()
    def _require_op(self):
        return self.channel.modes['op']
    def rehash(self):
        """Reconstruct matcher regex"""
        self.matchers = {   "JOIN":     re.compile(self.join_re % self.re_data, self.join_flags),
                            "KICK":     re.compile(self.kick_re % self.re_data, self.kick_flags),
                            "MODE":     re.compile(self.mode_re % self.re_data, self.mode_flags),
                            "PRIVMSG":     re.compile(self.privmsg_re % self.re_data, self.privmsg_flags),
                            "PART":     re.compile(self.part_re % self.re_data, self.part_flags),
                            "TOPIC":     re.compile(self.topic_re % self.re_data, self.topic_flags),
                            "NOTICE":     re.compile(self.notice_re % self.re_data, self.notice_flags)
                        }

        # API for adding stuff to this on the fly..
        self.handlers = {   "JOIN":     self.handle_join,
                            "KICK":     self.handle_kick,
                            "MODE":     self.handle_mode,
                            "PRIVMSG":  self.handle_privmsg,
                            "PART":  self.handle_part,
                            "TOPIC":  self.handle_topic,
                            "NOTICE":  self.handle_notice
                        }
    def want(self, msg):
        try:
            self.m = self.matchers[msg.event].search(msg.data_segment)
            if self.m:
                return True
            else:
                return False
        except KeyError:
            # We've been asked to handle something we're not aware of.. so we
            # probably don't want it...
            return False

        # TODO Delegate to overridable from instance

    def handle(self, msg):
        # We contruct this list at runtime, which makes the objects mutable,
        # whereas if it were constructed and stored, we would not be able to
        # alter them on the fly
        try:
            self.handlers[msg.event](msg)
        except KeyError:
            # No handler for this event
            pass

    def handle_privmsg(self, msg):
        self.noop()


    def handle_kick(self, msg):
        self.noop()

    def handle_join(self, msg):
        self.noop()

    def handle_mode(self, msg):
        self.noop()

    def handle_topic(self, msg):
        self.noop()

    def handle_part(self, msg):
        self.noop()

    def handle_notice(self, msg):
        self.noop()

    def noop(self, *args, **kwargs):
        pass

    def is_action(self, msg):
        if self.action_matcher.match(msg.data_segment):
            return True
        else:
            return False
    def on_load(self, *args, **kwargs):
        pass
 
def _exit():
    #template
    sys.exit()


class OurModules(object):
    data = {'default': []}
    nick = "dummynick"
    def __setitem__(self, key, value):
        if key not in self.data:
            for i in self.data['default']:
                value.append(i)
        self.data[key] = value
    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        else:
            return self.data['default']
    def dump(self):
       dmp = []
       for i in self.data:
           dmp.append("%s:" % i)
           dmp.append("[ %s ]" % (", ".join(repr(j(self, self)) for j in  self.data[i])))
       return dmp
    def __repr__(self):
       return "\n".join(dmp)

