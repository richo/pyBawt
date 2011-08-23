LOGFILE='pyBawt.log'

def with_log(func):
    def _(msg):
        fh = open(LOGFILE, 'a')
        func(msg, fh)
        fh.close()
    return _

@with_log
def log(msg, fh):
    if not msg.endswith("\n"):
        msg += "\n"
    fh.write(msg)

def error(msg):
    log("E: %s" % msg)

def info(msg):
    log("I: %s" % msg)

def warn(msg):
    log("W: %s" % msg)

def fixme(msg):
    log("X: %s" % msg)
