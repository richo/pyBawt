class ProdModule(BawtM2):
    privmsg_re = "prods %(nick)s"
    privmsg_flags = re.I
    _name = "ProdModule"

    def handle_privmsg(self, msg):
        self.parent.action(msg.replyto, "prods %(nick)s right back!" % {'nick': msg.nick})
