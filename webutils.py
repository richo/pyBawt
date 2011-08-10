import time
import os

## CONFIG

# Trailing slash is important.
webroot = "http://natalya.psych0tik.net/~pyBawt/"
docroot = "/home/pyBawt/public_html"

class PublicationError(Exception):
    pass

def publish(content, prefix="", suffix="txt"):
    name = ""
    if prefix:
        name += prefix + "_"
    name += "%i.%s" % (time.time(), suffix)
    try:
        fh = open(os.path.join(docroot, name), 'w')
        fh.write(content)
        fh.close()
        return webroot + name

    except IOError:
        raise PublicationError
