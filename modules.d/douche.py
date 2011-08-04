class DoucheModule(BawtM2):
    privmsg_re = "!douche"
    _name = "DoucheModule"
    def handle_privmsg(self, msg):
        args = msg.data_segment.split(" ")
        if len(args) > 1:
            self.parent.privmsg(msg.replyto, "%s: Stop being a douche" % (args[1]))

