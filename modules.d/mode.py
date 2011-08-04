class ModeModule(BawtM2):
    _name = "ModeModule"
    privmsg_re = "!mode"
    def handle_privmsg(self, msg):
        self.parent.privmsg(msg.replyto, self.channel.dump_modes())
