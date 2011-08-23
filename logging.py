import time

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

def fmt(msg):
    return "%s | %s" % (time.asctime(), msg)

def error(msg):
    log("E: %s" % fmt(msg))

def info(msg):
    log("I: %s" % fmt(msg))

def warn(msg):
    log("W: %s" % fmt(msg))

def fixme(msg):
    log("X: %s" % fmt(msg))
