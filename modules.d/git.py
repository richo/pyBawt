import ourgit

class GitModule(BawtM2):
    _name = "GitModule"
    privmsg_re = "^(!|%(nick)s:\s+)git ?([^ ].*)"
    def handle_privmsg(self, msg):
        cmd = self.m.group(2)
        if cmd:
            self.parent.privmsg(msg.replyto, ourgit.oneline(cmd))
    
