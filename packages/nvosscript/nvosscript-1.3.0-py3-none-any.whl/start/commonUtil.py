import os


def check_local_workspace():
    if not os.path.exists(os.path.expanduser(os.path.join("~", '.ndtcrc'))):
        os.mkdir(os.path.expanduser(os.path.join("~", '.ndtcrc')))
