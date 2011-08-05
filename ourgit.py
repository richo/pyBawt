import subprocess as sp

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
    branch = current_branch()
    p = sp.Popen(["/usr/bin/git", "pull"], stdout=sp.PIPE, close_fds=True)
    #(stdout, stdin) = (p.stdout, p.stdin)
    p.wait()
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
