import webutils as wb

class NoteModule(BawtM2):
    """A module for the storage and retrieval of notes"""
    _name = "NoteModule"
    _commands = ['store', 'clear', 'list']
    privmsg_re = "^(!|%(nick)s:\s?)(%(commands)s)" % {'commands': "|".join(_commands),
            'nick': '%(nick)s'}
    note_file = "note_data"

    @staticmethod
    def Notes():
        try:
            out = []
            for i in open(self.note_file, 'r').readlines():
                line = i.replace("\r", "").replace("\n", "")
                out.append(line)

            yield out

            fh = open(self.note_file, 'w')
            for i in out:
                fh.write(i + '\n')

        except IOError:
            pass

    def reply(self, msg, say):
        self.parent.privmsg(msg.replyto, "%s: %s" % (msg.nick, say))

    def handle_privmsg(self, msg):
        if not self.auth(msg):
            self.parent.privmsg(msg.replyto, "%s: I don't know you." % (msg.nick))
            return
        with Notes() as notes:
            argv = msg.data_segment.split(" ")
            if self.m.group(2) == "store":
                note = " ".join(argv[1:])
                if note:
                    if note in notes:
                        self.reply(msg, "Message already stored")
                    else:
                        notes.append(note)
                        self.reply(msg, "Stored.")
                else:
                    self.reply(msg, "!store <note>")
            elif self.m.group(2) == "clear":
                while notes:
                    notes.delete(0)
                self.reply(msg, "Message list cleared.")
            elif self.m.group(2) == "list":
                if not notes:
                    self.reply(msg, "I pity the fool who has no notes")
                    return
                try:
                    note_data = "\n".join(notes)
                    self.reply(msg, wb.publish(note_data))
                except wb.PublicationError:
                    self.reply("Couldn't publish note data")

