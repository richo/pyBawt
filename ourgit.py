import subprocess as sp

def update_git():
    p = sp.Popen(["/usr/bin/git", "fetch"], stdin=sp.PIPE, stdout=sp.PIPE, close_fds=True)
    (stdout, stdin) = (p.stdout, p.stdin)

def checkout_git(branch):
    pass

def update_git_head():
    pass

def version():
    pass

def log():
    pass

def clean_git():
    pass
