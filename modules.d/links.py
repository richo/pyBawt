# TODO Add some data directory in the next level up, and have the same
# mechanism that buidls everything in modules.d include it first, then put
# module data in there, to avoid this nasty mix of code and data in the module
# code.
#
# This should make it more feasible for 3rd party developers to use this, and
# may also motivate me to finally build a usable authentication layer

class LinkModule(BawtM2):
    "Translate links neatly"
    trips = ['!nat']
    # TODO Create a user class to hold all of this data along with GH repo etc
    usermap = {'richo': ('richo', 'rich0', 'warlawk', 'warl0ck'),
               'samurai': ('drewid', 'samurai', 'drewid[rogue]',
                   'drewid[nat]', 'TheLonelyPanda'),
               'carbon': ('CarbonLifeForm', 'm0nk')}
    # ^^ todo
    privmsg_re = "^(%(t)s) (.*)" % {'t': '|'.join(trips)}
    _name = "LinkModule"
    def handle_privmsg(self, msg):
        for user, nicks in self.usermap.iteritems():
            if msg.nick in nicks: 
                self.parent.privmsg(msg.replyto, "http://natalya.psych0tik.net/~%s/%s" % 
                        (user, self.m.group(2)))
                return
        self.parent.privmsg(msg.replyto, "%s: I'm fairly sure you don't have an account on natalya" % (msg.nick))



