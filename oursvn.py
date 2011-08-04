import subprocess as sp

def update_svn():
    p = sp.Popen(["/usr/bin/svn", "update"], stdin=sp.PIPE, stdout=sp.PIPE, close_fds=True)
    (stdout, stdin) = (p.stdout, p.stdin)
    data = stdout.readline()
    while data:
        if "revision" in data:
            break
        data = stdout.readline()
    stdout.close()
    stdin.close()
    out =  "%s -> %s" % (data, log())
    return out.replace("\n", "")

def version():
    try:
        p = sp.Popen(["/usr/bin/svnversion", "."], stdin=sp.PIPE, stdout=sp.PIPE, close_fds=True)
        (stdout, stdin) = (p.stdout, p.stdin)
        data = stdout.readline()
        stdout.close()
        stdin.close()
        return data
    except:
        return "No version data"

def log():
    try:
        p = sp.Popen(["/usr/bin/svn", "log", "-r", "BASE", "--xml"], stdin=sp.PIPE, stdout=sp.PIPE, close_fds=True)
        (stdout, stdin) = (p.stdout, p.stdin)
        data = stdout.readlines()
        stdout.close()
        stdin.close()
        for i in data:
            if i.startswith("<msg>"):
                return i.replace("<msg>", "").replace("\n", "")
    except:
        return "No version data"
