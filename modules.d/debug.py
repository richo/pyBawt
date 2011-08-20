class DebugModule(BawtM2):
    _name = "DebugModule"
    privmsg_re = "(!|%(nick)s:\s?)repr"
    def handle_privmsg(self, msg):
        print repr(msg.data_segment)
        self.parent.privmsg(msg.replyto, "%(nick)s: %(data)s" % {'nick': msg.nick,
            'data': repr(msg.data_segment)})

