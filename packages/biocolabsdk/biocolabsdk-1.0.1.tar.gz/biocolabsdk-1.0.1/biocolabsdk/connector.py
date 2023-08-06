import os
import pwd
import getpass
import json
import grp
import bioflex
from bioturing_connector.connector import BBrowserXConnector


class Identity():

    def __init__(self, user: str, group: str = None):
        self.uid = pwd.getpwnam(user).pw_uid
        if not group:
            self.gid = pwd.getpwnam(user).pw_gid
        else:
            self.gid = grp.getgrnam(group).gr_gid

    def __enter__(self):
        self.original_uid = os.getuid()
        self.original_gid = os.getgid()
        os.setegid(self.uid)
        os.seteuid(self.gid)

    def __exit__(self, type, value, traceback):
        os.seteuid(self.original_uid)
        os.setegid(self.original_gid)


class EConnector:
    """Create a connector object to submit/get data from BioColab
    """

    def __init__(self, public_token: str = "", private_host: str = "", private_token: str = ""):
        """
          Args:
            public_token:
              The API token to verify authority. Generated in https://talk2data.bioturing.com
            private_host:
              The URL of the BBrowserX server, only supports HTTPS connection
              Example: https://bbrowserx.bioturing.com
            private_token:
              The API token to verify authority. Generated in-app.
        """
        self.__public_token = public_token
        self.__private_host = private_host
        self.__private_token = private_token

    def empty(self, data: str):
        if (data is None) or (len(data) == 0):
            return True
        return False

    def get_system_user(self):
        try:
            user = pwd.getpwuid(os.getuid())[0]
        except:
            user = os.environ.get('NB_USER', getpass.getuser())
        return user

    def get_user_home_path(self):
        username = self.get_system_user()
        if username is None:
            return None

        pathDir = f"/home/{username}"
        try:
            with Identity(username):
                pathDir = os.path.expanduser(
                    f"~{pwd.getpwuid(os.geteuid())[0]}")
        except:
            pass

        return pathDir

    def get_settings(self):
        obj = {}
        user_home_path = self.get_user_home_path()
        if user_home_path is None:
            return obj

        bio_key_file = f"{user_home_path}/.bioapi.key"
        if os.path.exists(bio_key_file):
            with open(bio_key_file) as f:
                try:
                    obj = json.loads(f.read().strip())
                except:
                    pass
                f.close()

        return obj

    """
      Args:
        private_host:
          The URL of the BBrowserX server, only supports HTTPS connection
          Example: https://bbrowserx.bioturing.com
          If empty, BioColab will retrieve this information from your settings.
        private_token:
          The API token to verify authority. Generated in-app.
          If empty, BioColab will retrieve this information from your settings.
        ssl: SSL mode
    """

    def get_bbrowserx(
        self,
        private_host: str = "",
        private_token: str = "",
        ssl: bool = True
    ):
        host = private_host
        if self.empty(host) == True:
            host = self.__private_host

        token = private_token
        if self.empty(token) == True:
            token = self.__private_token

        if (self.empty(host) == True) or (self.empty(token) == True):
            try:
                contents = self.get_settings()
                if "bio_bbx_private_domain" in contents:
                    host = contents["bio_bbx_private_domain"]
                if "bio_bbx_private_key" in contents:
                    token = contents["bio_bbx_private_key"]
            except Exception as e:
                raise e

        if (self.empty(host) == True) or (self.empty(token) == True):
            raise Exception("Empty BBrowserX setting")

        return BBrowserXConnector(
            host=host,
            token=token,
            ssl=ssl
        )

    """
      Args:
        public_token:
          The API token to verify authority. Generated in https://talk2data.bioturing.com
          If empty, BioColab will retrieve this information from your settings.
    """

    def get_bioflex(
        self,
        public_token: str = ""
    ):
        token = public_token
        if self.empty(token) == True:
            token = self.__public_token

        if (self.empty(token) == True):
            try:
                contents = self.get_settings()
                if "bio_bbx_public_key" in contents:
                    token = contents["bio_bbx_public_key"]
            except Exception as e:
                raise e

        if (self.empty(token) == True):
            raise Exception("Empty BioFlex setting")

        return bioflex.connect(public_token)
