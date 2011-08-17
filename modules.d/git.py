import ourgit

class GitModule(BawtM2):
    _name = "GitModule"
    privmsg_re = "^(!|%(nick)s:\s+)git ?([^ ].*)"
    def handle_privmsg(self, msg):
        if parent.Authenticator.authed(msg.nick):
            cmd = 'git ' + self.m.group(2)
            if cmd:
                self.parent.privmsg(msg.replyto, ourgit.oneline(cmd))
        else:
            self.parent.privmsg(msg.replyto, "You are not authenticated")
