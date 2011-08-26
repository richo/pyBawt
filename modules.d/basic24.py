
# Begin HBH Basic24 code

import hashlib
import base64
import binascii
import logging
class Basic24Module(BawtM2):
    success_re = re.compile(r"[\r\n]{1,2}\s+QUIT", re.I)
    _commands = ['help', 'say', 'md5', 'b64', 'sha1', 'rot47', 'hex', 'rot47crack', 'b64crack', 'hex2ascii' ]
    privmsg_re = "^@(%s)" % ("|".join(_commands))
    badchars = ["\r", "\n", "\t", chr(8) ]
    _name = "Basic24Module"

    def bind_write(self, msg):
        def write(text):
            success = False
            # Test for a solution
            if self.success_re.search(text):
                success = True
            # Scrub some badchars..
            for i in self.badchars:
                text = text.replace(i, '')
            # Prefix with nick..?
            if not success:
                self.parent.privmsg(msg.replyto, "%(nick)s: %(text)s" % {'nick': msg.nick,
                                    'text': text })
            else:
                self.parent.privmsg(msg.nick, "%(nick)s: Well done, the password is... crlfOwnsYou" % {'nick': msg.nick})
        self.write = write

    @staticmethod
    def rot47(text):
        return ''.join([chr(33+((ord(c)-33+47)\
                %(47*2))) if c!=" "else " " for c in text])
    
    def handle_privmsg(self, msg):
        try:
            real_handle_privmsg(msg)
        except:
            logging.error("Fell on it's arse with %s" % (msg.dump()))
            raise

    def real_handle_privmsg(self, msg):
        self.bind_write(msg)
        argv = msg.data_segment.split(" ", 1)
        try:
            #  {{{ Handle arguments, delegate calls
            if argv[0] == "@help":
                self.do_help()
            else:
                try:
                    # Needs to be a PM...
                    if msg.replyto.startswith("#"):
                        self.write("You must play with the bot in pm's....")
                        return
                    if argv[0] == "@say":
                        self.do_say(argv[1])
                    elif argv[0] == "@md5":
                        self.do_md5(argv[1])
                    elif argv[0] == "@b64":
                        self.do_b64(argv[1])
                    elif argv[0] == "@sha1":
                        self.do_sha1(argv[1])
                    elif argv[0] == "@rot47":
                        self.do_rot47(argv[1])
                    elif argv[0] == "@hex":
                        self.do_hex(argv[1])
                    #elif argv[0] == "@md5crack":
                    #    self.do_md5crack(argv[1])
                    elif argv[0] == "@b64crack":
                        self.do_b64crack(argv[1])
                    #elif argv[0] == "@sha1crack":
                    #    self.do_sha1crack(argv[1])
                    elif argv[0] == "@rot47crack":
                        self.do_rot47crack(argv[1])
                    elif argv[0] == "@hex2ascii":
                        self.do_hex2ascii(argv[1])
                    else:
                        self.write("How on earth did you get here")
                    # }}}
                except:
                    msg.dump()
        except IndexError:
            self.write("That function requires an argument...")
    def do_help(self):
        helpstr = []
        for i in self._commands:
            helpstr.append("@"+i)
        self.write(", ".join(helpstr))
        self.write("Remember, the objective is to cause the bot to disconnect from the irc network")
    def do_say(self, text):
        self.write(text)
    def do_md5(self, text):
        self.write(hashlib.md5(text).hexdigest())
    def do_b64(self, text):
        self.write(base64.b64encode(text))
    def do_sha1(self, text):
        self.write(hashlib.sha1(text).hexdigest())
    def do_rot47(self, text):
        self.write(self.rot47(text))
    def do_hex(self, text):
        outs = ""
        for i in text:
            outs += "%x" % ord(i)
        self.write(outs)
    #def do_md5crack(self, text):
    #    self.write("md5crack")
    def do_b64crack(self, text):
        try:
            self.write(base64.b64decode(text))
        except TypeError:
            self.write("Invalid b64 data")
    #def do_sha1crack(self, text):
    #    self.write("sha1crack")
    def do_rot47crack(self, text):
        self.write(self.rot47(text))
    def do_hex2ascii(self, text):
        try: 
            self.write(binascii.unhexlify(text))
        except TypeError:
            self.write("Invalid hex data")
