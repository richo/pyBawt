import time
import random

class PenisModule(BawtM2):
    "8======D"
    timeout = 60
    timelast = None
    privmsg_re = "^!penis"
    _name = "PenisModule"
    def handle_privmsg(self, msg):
        if self.timelast and time.time() < (self.timelast + self.timeout):
            return
        self.timelast = time.time()
        self.parent.privmsg(msg.replyto, "%s: 8====%s====D" % (msg.nick, "="*random.randint(4,10)))
