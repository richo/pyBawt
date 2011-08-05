import ourgit

class GitModule(object):
    _name = "GitModule"
    privmsg_re = "^(!|%(nick)s:\s?)([^\\s].*)"
    def handle_privmsg(self, msg):
        cmd = self.m.group(2)
        if cmd:
            self.parent.privmsg(msg.replyto, ourgit.oneline(cmd))
    
