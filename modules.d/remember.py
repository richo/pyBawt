import webutils as wb

class Notes(object):
    def __init__(self, note_file):
        self.note_file = note_file

    def __enter__(self):
        try:
            self.out = []
            for i in open(self.note_file, 'r').readlines():
                line = i.replace("\r", "").replace("\n", "")
                self.out.append(line)
            return self.out
        except IOError:
            return []
    def __exit__(self, type, value, traceback):
        fh = open(self.note_file, 'w')
        for i in self.out:
            fh.write(i + '\n')


class NoteModule(BawtM2):
    """A module for the storage and retrieval of notes"""
    _name = "NoteModule"
    _commands = ['store', 'clear', 'list']
    privmsg_re = "^(!|%(nick)s:\s?)(%(commands)s)" % {'commands': "|".join(_commands),
            'nick': '%(nick)s'}
    note_file = "note_data_%s"

    def reply(self, msg, say):
        self.parent.privmsg(msg.replyto, "%s: %s" % (msg.nick, say))

    def handle_privmsg(self, msg):
        if self.auth(msg):
            limit = 5000
        else
            limit = 25
        with Notes(self.note_file % msg.nick) as notes:
            argv = msg.data_segment.split(" ")
            if self.m.group(2) == "store":
                if len(notes) > limit:
                    self.reply("Too many notes stored")
                    return
                note = " ".join(argv[1:])
                if len(note) > 256:
                    self.reply("Note too long")
                    return
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
                    del notes[0]
                self.reply(msg, "Message list cleared.")
            elif self.m.group(2) == "list":
                if not notes:
                    self.reply(msg, "I pity the fool who has no notes")
                    return
                try:
                    note_data = "\n".join(notes)
                    self.reply(msg, wb.publish(note_data))
                except wb.PublicationError:
                    self.reply(msg, "Couldn't publish note data")

