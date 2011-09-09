import subprocess as sp
import logging

def oneline(cmd):
    try:
        p = sp.Popen(cmd.split(" "), stdout=sp.PIPE, close_fds=True)
        p.wait()
        return p.stdout.readline()
    except OSError:
        return "Couldn't find binary (probably)"
def sp_stdout(cmd):
    try:
        p = sp.Popen(cmd.split(" "), stdout=sp.PIPE, close_fds=True)
        yield p.stdout
    except OSError:
        raise StopIteration

def current_branch():
    with sp_stdout('git branch') as branchout:
        while True:
            i = stdout.readline()
            if i.startswith("*"):
                return i[1:].strip()
        return False
        
def update_git():
    data = oneline("git pull")
    logging.info("Updated source to %s" % data)
    return data
    # TODO sanity check


def checkout_git(branch):
    return oneline('git checkout %s' % branch)

def update_git_head():
    return oneline('git reset --hard HEAD')

def version():
    return oneline('git show --shortstat HEAD')[:16]

def log():
    return ""

def clean_git():
    pass

def git(cmd):
    return oneline("git %s" % cmd)
    
