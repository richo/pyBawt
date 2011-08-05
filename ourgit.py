import subprocess as sp

def oneline(cmd):
    try:
        p = sp.Popen(cmd.split(" "), stdout=sp.PIPE, close_fds=True)
        p.wait()
        return p.stdout.readline()
    except OSError:
        return "Couldn't find binary (probably)"

def current_branch():
    p = sp.Popen(["/usr/bin/git", "branch"], stdin=sp.PIPE, stdout=sp.PIPE, close_fds=True)
    (stdout, stdin) = (p.stdout, p.stdin)
    while True:
        i = stdout.readline()
        if i.startswith("*"):
            return i[1:].strip()
    return False
#   TODO
        
def update_git():
    return oneline("git pull")
    # TODO sanity check


def checkout_git(branch):
    pass

def update_git_head():
    pass

def version():
    p = sp.Popen(["/usr/bin/git", "show", "--shortstat", "HEAD"], stdout=sp.PIPE, close_fds=True)
    stdout = p.stdout
    return stdout.readline()[:16]

def log():
    return ""

def clean_git():
    pass

def git(cmd):
    return oneline("git %s" % cmd)
    
