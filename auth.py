import hashlib
import pickle
import atexit
import logging

AUTH_FILE_NAME="authen.db"

class Authenticator(object):
    """\
An object that statefully keeps track of all authentication
It is managed by AuthModule which tracks the server messages
    """
    def __init__(self, auth_hash='', valid_host=''):
        self.auth_hash = auth_hash
        self.valid_host = valid_host
        # TODO Case insensitive
        self.authenticated = []
        self.load()
        atexit.register(self.save)

    def try_auth(self, msg, password):
        if msg.nick in self.authenticated:
            return True
        # Max kludge per user password
        if hashlib.md5(password).hexdigest() == self.auth_hash:
            self.authenticated.append(msg.nick)
            return True
        return False

    def revoke_auth(self, nick):
        count = 0
        try:
            while True:
                self.authenticated.remove(nick)
                count+=1
        except ValueError:
            return count > 0

    def authed(self, msg):
        return msg.nick in self.authenticated

    def save(self):
        pickle.dump(self.auth_data, open(AUTH_FILE_NAME, 'w'))
    def load(self):
        try:
            fh = open(AUTH_FILE_NAME, 'r')
            self.auth_data = pickle.load(fh)
        except IOError:
            self.auth_data = {}

    # TODO
    # Authentication decorator

