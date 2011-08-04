class LostyModule(BawtM2):
    privmsg_re = "losty"
    _name = "LostyModule"
    def handle_privmsg(self, msg):
        self.parent.privmsg(msg.replyto, "Losty is a raging faggot")

class BlipModule(BawtM2):
    privmsg_re = "blip"
    privmsg_flags = re.I
    _name = "BlipModule"
    def handle_privmsg(self, msg):
        self.parent.kick(msg.replyto, msg.nick, "I'll fucken blip you in a moment")
