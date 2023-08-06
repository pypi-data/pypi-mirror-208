from functools import lru_cache
import spgci.config as config
import requests
from requests.exceptions import HTTPError, SSLError
import warnings


@lru_cache()
def get_token(
    username: str = config.username,
    password: str = config.password,
    appkey: str = config.appkey,
    url: str = config.base_url,
) -> str:
    """
    Get an Access Token for API calls.\n

    *Does not need to be invoked in user code. Instead see ``config.set_credentials()``*

    Can be called without arguments if environment variables are set.

    Automatically caches token based on the arguments supplied.\n

    Parameters
    ----------
    username : str, optional
        username for calling APIs, by default config.username or `SPGCI_USERNAME`
    password : str, optional
        password for calling APIs, by default config.password or ``SPGCI_PASSWORD``
    appkey : str, optional
        appkey for calling APIs, by default config.appkey or ``SPGCI_APPKEY``
    url : str, optional
        base url, by default config.base_url

    Returns
    -------
    str
        Access Token
    """

    body = {
        "username": username,
        "password": password,
    }
    headers = {"appkey": appkey}

    url = f"{url}/auth/api"

    try:
        r = requests.post(
            url,
            data=body,
            headers=headers,
            verify=config.verify_ssl,
            proxies=config.proxies,
        )
        r.raise_for_status()
        return r.json()["access_token"]
    except SSLError as err:
        resp = err.response
        warnings.warn(
            "You can likely avoid this issue by setting `ci.config.verify_ssl = False`"
        )

        raise
    except HTTPError as err:
        resp = err.response
        if resp.status_code in [401, 403]:
            print(resp.status_code, resp.json())
            print("Try calling `set_credentials(<username>, <password>, <appkey>)`")

        raise
