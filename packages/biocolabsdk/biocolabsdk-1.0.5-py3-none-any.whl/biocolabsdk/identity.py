import grp
import os
import pwd

class Identity():

    def __init__(self, user: str, group: str = None):
        try:
            self.uid = pwd.getpwnam(user).pw_uid
            if not group:
                self.gid = pwd.getpwnam(user).pw_gid
            else:
                self.gid = grp.getgrnam(group).gr_gid
        except:
            pass

    def __enter__(self):
        try:
            self.original_uid = os.getuid()
            self.original_gid = os.getgid()
            os.setegid(self.uid)
            os.seteuid(self.gid)
        except:
            pass

    def __exit__(self, type, value, traceback):
        try:
            os.seteuid(self.original_uid)
            os.setegid(self.original_gid)
        except:
            pass