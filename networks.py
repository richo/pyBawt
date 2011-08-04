default = 'irc.psych0tik.net'

class ircnet(object):
    """Just holds some data memebers"""
    port = 6667
    ssl = False
    host = ''
    nick = 'pyBawt'
    def __init__(self, host, port, ssl=False, nick='pyBawt',
            auth_host='', auth_hash=''):
        self.port = port
        self.ssl = ssl
        self.host = host
        self.nick = nick
        self.auth_host = auth_host
        self.auth_hash = auth_hash

networks = {
    'irc.psych0tik.net':    ircnet('irc.psych0tik.net', 6697, ssl=True, auth_host = "staffers.psych0tik.net", auth_hash="85fa67a2beebfc9a7cdc2d572af65b4b"),
    'irc.dal.net':          ircnet('irc.dal.net', 6667, ssl=False)
}


