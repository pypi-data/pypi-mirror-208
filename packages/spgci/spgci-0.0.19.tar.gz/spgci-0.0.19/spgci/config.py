"""
Configure SPGCI settings
"""
import os
from typing import Dict

#: Username to use with the SPGCI API
username: str = os.getenv("SPGCI_USERNAME", "")
#: Password to use with the SPGCI API
password: str = os.getenv("SPGCI_PASSWORD", "")
#: Appkey to use with the SPGCI API
appkey: str = os.getenv("SPGCI_APPKEY", "")

#: Set the base url used when making HTTP calls
base_url = "https://api.platts.com"
#: Set `verify` to `False` when making HTTP calls
verify_ssl = True
#: Add proxy to HTTP calls
proxies: Dict[str, str] = {}

#: Version of the SPGCI Pkg
version = "0.0.19"

#: time to sleep between api calls
sleep_time = 0


def set_credentials(un: str, pw: str, apikey: str) -> None:
    """
    Set credentials to use when calling the SPGCI API.

    You can avoid calling `set_credentials` by setting environment variables or creating a ``.env`` file with the following structure:\n
    SPGCI_USERNAME=``username``\n
    SPGCI_PASSWORD=``password``\n
    SPGCI_APPKEY=``appkey``\n

    Parameters
    ----------
    un : str
        username
    pw : str
        password
    apikey : str
        appkey
    """
    global username, password, appkey
    username = un
    password = pw
    appkey = apikey
