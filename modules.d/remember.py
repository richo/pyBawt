import webutils as wb

class NoteModule(BawtM2):
    """A module for the storage and retrieval of notes"""
    _name = "NoteModule"
    _commands = ['store', 'clear', 'list']
    privmsg_re = "^(!|%(nick)s:\s?)(%(commands)s)" % {'commands': "|".join(_commands),
            'nick': '%(nick)s'}
    note_file = "note_data"
    def __init__(self, parent, channel):
        BawtM2.__init__(self, parent, channel)
        self.notes = []
        self.read_notes()

# Notefile handlers {{{
    def read_notes(self):
        try:
            for i in open(self.note_file, 'r').readlines():
                line = i.replace("\r", "").replace("\n", "")
                self.notes.append(line)
        except IOError:
            pass

    def write_notes(self):
        # We shoudl append/clobber instead of rewriting
        try:
            fh = open(self.note_file, 'w')
            for i in self.notes:
                fh.write(i + '\n')
            return True
        except IOError:
            return False
# }}}

    def reply(self, msg, say):
        self.parent.privmsg(msg.replyto, "%s: %s" % (msg.nick, say))

    def handle_privmsg(self, msg):
        if not self.auth(msg):
            self.parent.privmsg(msg.replyto, "%s: I don't know you." % (msg.nick))
            return
        argv = msg.data_segment.split(" ")
        if self.m.group(2) == "store":
            note = " ".join(argv[1:])
            if note:
                if note in self.notes:
                    self.reply(msg, "Message already stored")
                else:
                    self.notes.append(note)
                    self.reply(msg, "Stored.")
            else:
                self.reply(msg, "!store <note>")
            self.write_notes()
        elif self.m.group(2) == "clear":
            self.notes = []
            self.reply(msg, "Message list cleared.")
            self.write_notes()
        elif self.m.group(2) == "list":
            if not self.notes:
                self.reply(msg, "I pity the fool who has no notes")
                return
            try:
                note_data = "\n".join(self.notes)
                self.reply(msg, wb.publish(note_data))
            except wb.PublicationError:
                self.reply("Couldn't publish note data")

