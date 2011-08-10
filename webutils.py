import time
import os

## CONFIG

# Trailing slash is important.
webroot = "http://natalya.psych0tik.net/~pyBawt/"
docroot = "/home/pyBawt/public_html"

class PublicationError(Exception):
    pass

def publish(content, prefix=""):
    name = ""
    if prefix:
        name += prefix + "_"
    name += "%i" % time.time()
    try:
        fh = open(os.path.join(docroot, name))
        fh.write(content)
        fh.close()
        return webroot + name

    except OSError:
        raise PublicationError
