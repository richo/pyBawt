import mpd
import signal

class RadioModule(BawtM2):
    """Houses everything to do with the radio"""
    _commands = ['current', 'url', 'something']
    topic_re = "."
    privmsg_re = "^(!|%(nick)s:\s?)(%(commands)s)" % {'commands': "|".join(_commands),
            'nick': '%(nick)s'}
    _name = "RadioModule"
    def __init__(self, parent, channel):
        # Overloaded to allow us to bind our signal
        BawtM2.__init__(self, parent, channel)

        parent.reg_handler(signal.SIGALRM, self.update_song)
        # This is not the place to be doing misc channel specfic stuff like
        # getting ops.  Put this in channel.py. Or something. Even if it just
        # means calling a func that's defined here, from there.

        self.topic_prefix = "psych0tik radio"
        self.topic_suffix = "http://radio.psych0tik.net/FAQ.py"


    def update_song(self):
        topic = "%s || %s || %s" % (self.topic_prefix, self.str_current_song(), self.topic_suffix)
        if not self.channel.set_topic(topic):
            self.channel.privmsg("Dammit I needz teh ops!")

    def str_current_song(self):
        reply = "Now playing %(title)s by %(artist)s"
        return reply % self.current_song()

    def current_song(self):
        blank = {   'album': 'Unknown Album', #{{{ Blank template data
                    'composer': 'Unknown Compose',
                    'artist': 'Unknown Artist',
                    'track': '0',
                    'title': 'Unknown Track',
                    'pos': '0',
                    'last-modified': 'Unknown Date',
                    'albumartist': 'Unknown Artist',
                    'file': 'Unknown File',
                    'time': '0',
                    'date': 'Unknown Date',
                    'genre': 'Unknown Genre',
                    'id': '0'} #}}}
        client = mpd.MPDClient()
        client.connect("domino.psych0tik.net", 6600)
        data = client.currentsong()
        client.close()
        client.disconnect()
        blank.update(data)
        return blank

    def handle_topic(self, msg):
        """This will get confused if there aren't two sets of || in the topic
        So we just drop it if that happens"""
        # Radio topic updating disabled until radio comes back up
        return
        if msg.nick == self.parent.nick:
            # Otherwise we'll be here all day.
            return
        new = msg.data_segment
        if new.count("||") < 2:
            self.parent.privmsg(msg.address_segment, "%s: Sorry, you must include the || markers in the topic" % msg.nick)
        else:
            self.topic_prefix, song, self.topic_suffix = new.split("||", 2)
            self.topic_prefix, self.topic_suffix = self.topic_prefix.strip(), self.topic_suffix.strip()
        self.update_song()


    def handle_privmsg(self, msg):
        # TODO - Put checking this in the event cue somehow?
        # TODO - Timeout on connections
        if self.m.group(2) == "url":
            self.parent.privmsg(msg.replyto, "%s: http://radio.psych0tik.net/hax.ogg.m3u" % (msg.nick))

        elif self.m.group(2) == "current":
            reply = "Now playing %(title)s by %(artist)s off %(album)s" % self.current_song()
            self.parent.privmsg(msg.replyto, "%s: %s" % (msg.nick, reply))

# TODO
# commands:
# url last10 last5
# next?
# Some degree of admin control
