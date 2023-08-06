"""Token Generation module."""
import os
from datetime import datetime
from time import time
from paramiko import RSAKey, ssh_exception
from getpass import getpass
from io import StringIO
import requests
import warnings
import jwt
import sys
import json
import logging

LOG = logging.getLogger(__name__)


class TokenCreater:
    """Generate Token for the API CALLs"""

    def __init__(self) -> None:
        """Initiate the Token URL for token authentication."""
        self.TOKEN_EXCHANGE_URL = "https://{}/oauth2/1.0/token"
        self.current_token = None
        self.token_datetime = None

    @staticmethod
    def _fatal(message):
        LOG.error("Error: {}".format(message), file=sys.stderr)
        sys.exit(1)

    def _get_access_token(self, id_token, host):
        # Ignore the "Unverified HTTPS request is being made." warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = {
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token": id_token,
                "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
            }
            response = requests.post(
                self.TOKEN_EXCHANGE_URL.format(host), data=data, verify=False
            )
            response.close()
            if response:
                response = response.json()
                if "access_token" in response:
                    return response["access_token"]
            self._fatal("Failed to get proper access token:\n{}".format(response))

    def _generate_id_token(self, aud, kid, iss, sub, private_key, expire_hours=24):
        addtl_header = {
            "kid": kid,
        }
        payload = {
            "aud": aud,
            "sub": sub,
            "iss": iss,
            "iat": int(time()),
            "exp": int(time()) + expire_hours * 3600,
        }
        new_jwt = jwt.encode(
            payload, private_key, algorithm="RS256", headers=addtl_header
        )
        return new_jwt

    def _get_private_key(self, key_file_name, password=None):
        try:
            rsa_key = RSAKey.from_private_key_file(key_file_name, password)
        except ssh_exception.PasswordRequiredException:
            password = getpass(prompt="Private key password: ")
            return self._get_private_key(key_file_name, password)
        except ssh_exception.SSHException:
            self._fatal("Invalid private key password")
        except FileNotFoundError:
            self._fatal(
                f"Could not find private key file :: { os.path.abspath(key_file_name) }"
            )
        with StringIO() as buf:
            rsa_key.write_private_key(buf)
            return buf.getvalue()

    def token_generation(
        self,
        client_id: str,
        key_id: str,
        client_name: str,
        key_file_private: str,
        username: str,
        fa_fqdn_ip: any,
        password=None,
        output_file=None,
    ) -> str:
        """Generation of the Token.

        Args:
            client_id (str): Client ID created on PureStorage for API calls
            key_id (str): Key ID generated on PureStorage while creating client ID for API calls
            client_name (str): Client Name created for the api call
            key_file_private (str): location of the private key file
            username (str): username of the purestorage
            fa_fqdn_ip (any): FQDN of the PureStorage
            password (_type_, optional): password of the pure storage. Defaults to None.
            output_file (_type_, optional): Location of file if the file need to be redirected. Defaults to None.

        Returns:
            str: :Provide the token for API call
        """
        date_strftime_format = "%d-%b-%y %H:%M:%S"
        pri_key = self._get_private_key(key_file_private, password)
        id_token = self._generate_id_token(
            client_id, key_id, client_name, username, pri_key
        )
        access_token = self._get_access_token(id_token, fa_fqdn_ip)
        self.current_token_modify(new_token=access_token)
        creation_datetime = datetime.now()
        self.token_create_datetime(
            token_cdatetime=creation_datetime.strftime(date_strftime_format)
        )
        if output_file:
            self.token_output_file(output_file)
        return access_token

    def current_token_modify(self, **kwarg):
        """Updating the token of the instance on the new token request.

        Returns:
            str: provide the new token.
        """
        if "new_token" in kwarg.keys():
            self.current_token = kwarg["new_token"]
        return self.current_token

    def token_create_datetime(self, **kwarg):
        """Provide date and time of the token creation.

        Returns:
            datetime: date and time of token creation
        """
        if "token_cdatetime" in kwarg.keys():
            self.token_datetime = kwarg["token_cdatetime"]
        return self.token_datetime

    def token_output_file(self, output_file):
        """Perform the write operation on a file.

        Args:
            output_file (str): filename need to be written with information.
        """
        with open(output_file, "w") as file:
            file.write(self.current_token)
            LOG.info("Access Token written to {}".format(file.name))

    def token_output_json(self, output_file):
        """Perform the write operation on a file in json format.

        Args:
            output_file (str): filename need to be written with information.
        """
        with open(output_file, "w") as jsonfile:
            json.dump(self.token_jsonformat(), jsonfile)

    def token_jsonformat(self):
        """format data with token and creation date.

        Returns:
            dict: dictory information of token and creation date
        """
        token_dic = {}
        token_dic["token"] = self.current_token
        token_dic["cdate"] = self.token_create_datetime()
        return token_dic
