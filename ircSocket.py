import threading
import socket
import sys
import time
import ssl
import re
# Rebuild module tree
import regen_modules
regen_modules.rebuild_bModules()
import bModules
import config
import signal
import auth

class ModuleError(Exception):
    pass

class IrcDisconnected(Exception):
    pass

class IrcTerminated(Exception):
    pass
class FlushQueue(Exception):
    """ Flush the event queue, don't wait for IO"""
    pass
class ModulesDidntLoadDueToSyntax(Exception):
    def __nonzero__(self):
        # This allows us to retain the logical "if status" test.
        return False

def should_reconnect():
    """This hook lies in here because it'll give the rest of the structure a fairly central place
    to pull strings from to arrange whether or not to do shit"""
    return True

# These calls need to be abstracted further, if I can do that then I can convince this module
# to update itself on the fly

Modules = {}

def mangle(name):
    if len(name) < 8:
        name += "_"
    else:
        name = name[:6] + "00"
    return name

def _load_modules():
    global Modules
    global bModules
    # This hook generates our bModules instance.
    regen_modules.rebuild_bModules()

    # Test for syntax errors...
    try:
        bModules = reload(bModules)
    except SyntaxError as e:
        tb = sys.exc_info()[2]
        exc_type, exc_value, exc_tb = sys.exc_info()
        raise ModulesDidntLoadDueToSyntax(exc_type, exc_value, exc_tb)
    Modules = bModules.modules
_load_modules()

#RE_NICK_MATCH = re.compile(r":([A-Za-z0-9_-^`]+)!([A-Za-z0-9_-]+)@([A-Za-z0-9_\.-])")
RE_NICK_MATCH = re.compile(r":([A-Za-z0-9\[\]\^\\~`_]+)!([~A-Za-z0-9]+)@([A-Za-z0-9_\.-]+)")
RE_INFO_MATCH = re.compile(r":([A-Za-z0-9\[\]\^\\~`_]+)!([~A-Za-z0-9]+)@([A-Za-z0-9_\.-]+)")

# This should both be a global AND a classmethod..
def is_private(msg):
    try:
        return not msg.address_segment.startswith("#")
    except:
        # Moar hax, don't test with objects without an address
        return False

class irc_data(object):
    def __init__(self, data):
        self.data = data

    def __eq__(self, cmp):
        if type(cmp) == int:
            return self.data == cmp
        elif type(cmp) == str:
            return str(self.data) == cmp
        else:
            return self.data == cmp
IRC_MOTD_START = irc_data(375)
IRC_MOTD_DATA = irc_data(372)
IRC_NICK_IN_USE = irc_data(433)
IRC_NICK_NOT_AVAILABLE = irc_data(432)
IRC_TOPIC = irc_data(332)


class Message(object):
    def __init__(self, msg):
        self.msg = msg
        self.data_segment = None
        self.address_segment = None
        self.nick = None
        self.name = None
        self.host = None
        self.numeric = False
        self._debug = False
        self.source, self.event, self.data = msg.split(" ", 2)
        self.event = self.event.upper()
        self.replyto = None
        self.origin = None
        try:
            int(self.event)
            self.numeric = True
            if ":" in self.data:
                self.address_segment, self.data_segment = [i.strip() for i in self.data.split(":", 1)]
        except ValueError:
            # For the most part, we can safely only look at stuff that's non-numeric
            # Implies that self.event wasn't a number
            if ":" in self.data:
                self.address_segment, self.data_segment = [i.strip() for i in self.data.split(":", 1)]
            else:
                self.data_segment = self.data
            # We go a bit further in attempting to gather info...
            #:richo!richo@staffers.psych0tik.net
            m = RE_NICK_MATCH.search(self.source)
            if m:
                self.nick = m.group(1)
                self.name = m.group(2)
                self.host = m.group(3)
        # Hax to make this slightly more logical
        if self.event == "JOIN":
            self.address_segment = self.data_segment
        # Hanlder hax
        if self.event == "MODE":
            self.address_segment = self.data_segment.split(" ", 1)[0]
        if is_private(self):
            self.replyto = self.nick
            self.origin = 'privmsg'
        else:
            self.replyto = self.address_segment
            self.origin = self.address_segment

        def parse_modes(self):
            if self.event != "MODE":
                return None
            channel, modes, nicks = self.data_segment.split(" ", 2)
            return (channel, modes, nicks)

    def __str__(self):
        return self.msg
    def dump(self):
        print "Data Segment    : %s" % (self.data_segment)
        print "Address Segment : %s" % (self.address_segment)
        print "Source          : %s" % (self.source)
        print "Event           : %s" % (self.event)
        print "Data            : %s" % (self.data)
        print "Nick            : %s" % (self.nick)
        print "Name            : %s" % (self.name)
        print "Host            : %s" % (self.host)
        print "--"

class chatnet(object):
    def __init__(self, host, port=6667, use_ssl=False):
        self.auth_host = ''
        self.auth_hash = ''
        self.nick = ""
        self._debug = False

        self.auth_host = config.auth_host
        self.auth_hash = config.auth_hash
        self.authenticator = auth.Authenticator(auth_hash = self.auth_hash, valid_host = self.auth_host)

        self.ready_signal = IRC_MOTD_START
        self.ready = False
        self.data = ""
        self._queue = []
        self.queue = []
        self.host = host
        self.port = port
        self.use_ssl  = use_ssl
        self.channels = {'privmsg': Channel("privmsg", self)}
        self.sock = SockConnect(self.host, self.port, self.use_ssl)
        self.msg  = self.privmsg
        self.chore_queue = []
        self.event_handlers = {
                'JOIN': self.handle_join
                }
    
    def recv_wait(self):
#This method pulls data back from the server and queues it for processing.
#So far it's considerations are:
#Don't do anything particularly clever with the last item, it may be incomplete
#Handle PING/PONG instantly.
#XXX TODO
        buf = self.sock.recv(1024)
        if not buf:
            raise IrcDisconnected
        self.data += buf
        self._queue += self.data.split("\r\n")
        if self.data.endswith("\r\n"):
            self.data = ""
        else:
            self.data = self._queue.pop()
        # continue with execution
    
    def _handle(self, msg):
# XXX This desperately needs fleshing out
# if addressed to channel 
#  -> locate channel object and add to queue
#  -- If not joined to channel, add channel object and populate queue
#  -> if in doubt, dump to main queue
#  -> Debug condition, self.debug everything-

# The _handle method also need

        if msg.upper().startswith("PING"):
            self.write(msg.upper().replace("PING", "PONG"))
            return
        message = Message(msg)
        # Have code for catching identify here.
        # IF ident successful
        # -> Set self.nick
        # IF ident failed
        # -> Mangle nick and try again. ## NEEDS NICK TO DO THIS. Set nick in identify
        if message.event == IRC_TOPIC:
            self.handle_topic(message)
        if message.event == IRC_NICK_IN_USE:
            self.retry_identify()
        if message.event == IRC_NICK_NOT_AVAILABLE:
            self.retry_identify()

        if message.event == self.ready_signal:
            self.ready = True

        # Start handling.
        # TODO, do whatever hax need to be done to populate the channel's topic element.
        # Perfectly valid to have the channel itself put in a request for the topic in initialisation

        if message.event in self.event_handlers:
            self.event_handlers[message.event](message)

        try:
            chan = self.channels[message.address_segment]
            chan.add_msg(message)
        except:
            # This creates channels for EVERYONE that privmsg's us.
            # I'm not sure this is right, should privmsg's from nonchannels just go into an arbitrary queue?
            # Ignore stuff for channels we don't know about.
            self.channels['privmsg'].add_msg(message)
    def handle_join(self, msg):
        self.add_channel(msg.data_segment)

    def handle_topic(self, msg):
        #Source          : :natalya.psych0tik.net
        #Event           : 332
        #Data            : pyBawt_ #rawptest :OBVIOUS TOPIC STRING
        nick, chan = msg.address_segment.split(" ")[0:2]
        topic = msg.data_segment
        if chan in self.channels:
            self.channels[chan].topic = topic

    def add_channel(self, channel):
        if channel not in self.channels:
            self.channels[channel] = Channel(channel, self)

    def dump_queue(self):
        while self._queue:
            msg = self._queue.pop(0)
            if not msg:
                continue
            self._handle(msg)
        for i in self.channels.values():
            i.do_chores()
        self._do_chores()

    def dump_channel_data(self):
        out = []
        for i in self.channels:
            out.append(i)
            out.append(repr(self.channels[i].modules))
        return out

    def debug(self, msg):
        if self._debug:
            print msg

    def available_modules(self):
        out = []
        for i in dir(bModules):
            if i.endswith("Module"):
                out.append(i)
        return out

    def retry_identify(self):
        # We have been denied our nick, work out what to do.
        if self.nickserv_info:
            # We have nickserv info, so try to boot our ghost, however
            # We need a valid nick to do this. TODO
            pass
        else:
            self.identify(mangle(self.nick), self.nickserv_info)
            # This call is precariously close to becoming recursive.
            # Make sure that identify never has a direct call path here.
        
    def auth_self(self, to, pas):
        # privmsg bypasses the chores code, it seems
        self.add_chore(self.privmsg, (to, "IDENTIFY %s" % pas))

    def identify(self, nick, nickserv_info=None):
        # TODO Have this do something a bit more intelligent
        # If setting nick fails (trigger based on the queue, try again)
        # Use the chore system
        self.nickserv_info = nickserv_info
        self.nick = nick
        # We use _write because if we wait for readyness we'll be waiting a while..
        self._write("USER %(nick)s * 8 :%(nick)s"    % {"nick": nick})
        self._write("NICK %(nick)s"                  % {"nick": nick})
        # If we have ended up here and we have nickserv_info, one of two things has happened.
        # a) our nick is taken and we need to change nick, so we can talk to nickserv, then arrange a call to this function
        #    to get our nick back and ID
        # b) We have our nick (either because it was free or because we have ghosted our old nick)
        # Either way, that should be handled out of _handle for an appropriate signal, potentially off the MOTD signal
        # That tells us that we're ready
        if self.nickserv_info:
            self.ns_identify

    def notice(self, to, msg):
        # Should this be in the queue?
        self.write("NOTICE %(to)s :%(msg)s"       % {"to": to, "msg": msg})

    def privmsg(self, to, msg):
        self._write("PRIVMSG %(to)s :%(msg)s"       % {"to": to, "msg": msg})

    def action(self, to, msg):
        self._write("PRIVMSG %(to)s :\x01ACTION %(msg)s\x01" % {"to": to, "msg": msg})

    def kick(self, chan, nick, reason=''):
        self.write("KICK %(chan)s %(nick)s :%(reason)s" % (
            {   'chan':     chan,
                'nick':     nick,
                'reason':   reason}))

    def write(self, msg):
        self.add_chore(self._write, [msg])

    def _write(self, msg):
        self.sock.send(msg + "\n")

    def join(self, chan, key=""):
        self.add_chore(self._join, [chan, key])

    def part(self, chan, reason=""):
        self.add_chore(self._part, [chan, reason])


    def _part(self, chan, reason):
        self._write("PART %(chan)s %(reason)s" % {'chan': chan, 'reason': reason})
        # XXX Let a handler do this when we get notification from the server
        # it should tell us our state, not let us dictate
        if chan in self.channels:
            del self.channels[chan]

    def quit(self, quitmsg=""):
        # Flush our queues before we leave.
        self.write("QUIT :%s" % (quitmsg))
        self._do_chores()
        SockClose(self.sock)

    def reload_modules(self):
        """Reloads modules, returns true on success or a traceback object if shit hits the fan"""
        try:
            _load_modules()
        except ModulesDidntLoadDueToSyntax as tb:
            # TODO - this can't be right. Works, but looks all fucked up
            # I'm positive that the native exception handling caters for this
            return tb # Exception instance, contains exc_info
        else:
            for i in self.channels.values():
                i.reload_modules()
            return True
    def reg_handler(self, signum, handler):
        # Create a signal handler which inserts a call to handler into the chore stack
        def _(*args):
            # This is the function which will be called
            self.add_chore(handler, [])
            raise FlushQueue
        signal.signal(signum, _)

    def add_chore(self, method, args):
        self.chore_queue.append((method, args))

    def add_module(self, chan, module):
        return self.channels[chan].add_module(module)

    def del_module(self, chan, module):
        try:
            self.channels[chan].del_module(module)
        except ModuleError:
            print "Couldn't remove %s from %s" % (module, chan)
            raise

    def _join(self, chan, key=""):
        if chan not in self.channels:
            self.write("JOIN %(chan)s %(key)s" % {"chan": chan,
                                                  "key" : key})

            # self.channels[chan] = channel()
            # The recv parser will handle adding it, once we're actually joined.

    def _do_chores(self):
        ret = False
        if not self.ready:
            return
        while self.chore_queue:
            ret = True
            chore = self.chore_queue.pop(0)
            chore[0](* chore[1])
        return ret

class Nick(object):
    # Dummy holder for nick properties
    op = False
    voice = False

class Channel(object):
    """Placeholder until I actually have something of use"""
    def __init__(self, name, parent):
        self.name = name.lower()
        self.parent = parent
        self.queue = []
        self.mode = []
        self.cmode = []
        self.standing = []
        self.modules = []
        self.init_modules()
        self.topic = ""
        #self.get_topic()
        self.modes = {
                'op': False,
                'halfop': False,
                'voice': False,
                'owner': False,
                'admin': False
                }

    def privmsg(self, msg):
        """Hook for passing messages back when I have a channel, but not a parent"""
        self.parent.privmsg(self.name, msg)
    def mode_plus_b(self):
        self.mode(self.nick, "+B")

    def init_modules(self):
        try:
            for i in Modules[self.name]:
                self.modules.append(i(self.parent, self))
        except KeyError:
            # No modules for this channel..
            pass
    def get_topic(self):
        """Fire off a request for topic. This will be interpreted elsewhere"""
        self.parent.write("TOPIC %(name)s" % {'name': self.name})

    def set_topic(self, topic):
        """Set the topic for this channel"""
        self.parent.write("TOPIC %(name)s :%(topic)s" % {'name': self.name, 'topic': topic})
        # TODO - Need to retrieve channel modes
        # no +t means we don't need ops
        return self.modes['op']

    def reload_modules(self):
        _load_modules()
        self.modules = []
        self.init_modules()

    def add_module(self, module):
        try:
            self.modules.append(getattr(bModules, module)(self.parent, self))
            return True
        except AttributeError:
            return False

    def dump_modules(self):
        return ", ".join(repr(i) for i in self.modules)

    def del_module(self, module):
        m = getattr(bModules, module)
        l = len(self.modules)
        self.modules[:] = [i for i in self.modules if type(i) != type(m)]
        if len(self.modules) == l:
            raise ModuleError
        return
    
    def add_msg(self, msg):
        self.queue.append(msg)

    def handle_mode(self, msg):
        m_map = {'+': True, '-': False}
        o_map = {'o': 'op',
                 'v': 'voice',
                 'h': 'halfop',
                 'a': 'admin',
                 'q': 'owner'}
        try:
            chan, modes, nicks = msg.data_segment.split(" ", 2)
        except:
            # I don't know why non-channel mode events are winding up here
            return
        nicks = nicks.split(" ")
        action = 'True'
        for m in modes:
            try:
                action = m_map[m]
            except KeyError:
                nick = nicks.pop(0)
                try:
                    if nick == self.parent.nick:
                        self.modes[o_map[m]] = action
                    else:
                        # TODO do something clever when other people's modes are changed.
                        pass
                except KeyError:
                    # unrecognised mode.
                    print "Unrecognised mode!"
                    msg.dump()
    def dump_modes(self):
        return "%s: %s" % (self.name, repr(self.modes))

    def do_chores(self):
        # We load through a set of pluggable triggers.
        # I have not done this yet, but I'm gunna....
        while self.queue:
            msg = self.queue.pop(0)
            # Handle mode changes internally to update status
            if msg.event == "MODE":
                self.handle_mode(msg)
            for i in self.modules:
                if i.want(msg):
                    try:
                        # TODO - implement a signal stop
                        i.handle(msg)
                    except bModules.StopHandling:
                        break

def SockConnect(host, port, use_ssl):        
    addr = (host, port)
    sock = None
    for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            sock = socket.socket(af, socktype, proto)
            if use_ssl:
                sock = ssl.wrap_socket(sock)
        except socket.error, msg:
            sock = None
            continue
        try:
            sock.connect(sa)
        except socket.error, msg:
            sock.close()
            sock = None
            continue
        break
    if sock is None:
        raise RuntimeError, "could not connect socket"
    #sock.settimeout(1)
    return sock

def SockClose(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    except:
        pass
