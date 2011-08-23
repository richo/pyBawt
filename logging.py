LOGFILE='pyBawt.log'
fh = open(LOGFILE, '-a')

def log(msg):
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
