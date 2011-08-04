class GreetModule(BawtM2):
    _name = "GreetModule"
    def handle_join(self, msg):
        # We get notified of our own joins..
        if msg.nick != self.parent.nick:
            self.parent.privmsg(msg.replyto, "Hi %s" % msg.nick)

class WildModule(BawtM2):
    _name = "WildModule"
    def handle_join(self, msg):
        if self.parent.nick.lower() == "a":
            self.parent.action(msg.replyto, "wild %s appears!" % msg.nick)
    def on_load(self, *args, **kwargs):
        self.parent.identify('A')

