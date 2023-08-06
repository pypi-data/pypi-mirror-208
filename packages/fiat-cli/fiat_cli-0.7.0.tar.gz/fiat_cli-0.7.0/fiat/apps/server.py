import datetime as dt
import json
import os
from enum import Enum

import requests
from typer import Abort

from fiat.apps.utils import get_logger

current_path = os.getcwd()
logger = get_logger()


class FiatBackendRequest(Enum):
    Auth = "/api/auth/token"
    EnvdCreate = "/envd/create"
    EnvdDelete = "/envd/delete"
    DFSCreate = "/juicefs/create"
    DFSDelete = "/juicefs/delete"


def get_server_conf(path: str | None = None):
    target_path = f"{current_path}/fiat.json" if not path else path
    with open(target_path) as file_obj:
        server_conf = json.load(file_obj)['server']

    logger.debug(f"Server config loaded: {server_conf}")

    return server_conf


def dump_token_and_expire(data: dict):
    expire = dt.datetime.now() + dt.timedelta(minutes=14)
    data['expire'] = expire.isoformat()

    try:
        with open(f"{current_path}/auth.json", "w+", encoding="utf-8") as file_obj:
            json.dump(data, file_obj)
    except IOError:
        logger.error("Dumping 'auth.json' file failed!")
        raise Abort()

    return data


def authentication_with_server(
        server_conf: dict,
        password: str
):
    username = f"{server_conf['info']['username']}:{server_conf['info']['email']}"
    auth_body = {
        "grant_type": "password",
        "username": username,
        "password": password
    }
    auth_rsp = requests.post(
        url=f"{server_conf['host']}/api/auth/token",
        data=auth_body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if auth_rsp.status_code == 401:
        logger.error("User unauthorized! Please check your information and password.")
        raise Abort()
    elif auth_rsp.status_code != 200:
        logger.error(f"Authentication failed with status code: {auth_rsp.status_code}")
        raise Abort()

    # dump token & expire time
    auth_data = dump_token_and_expire(auth_rsp.json())

    return auth_data


def send_request_to_backend(
        api: FiatBackendRequest,
        password: str | None = None,
        payload: dict | None = None,
        query: dict | None = None
):
    server_conf = get_server_conf()

    # Get Auth token
    if password:
        auth_data = authentication_with_server(
            server_conf=server_conf,
            password=password
        )
    else:
        with open(f"{current_path}/auth.json", "r+") as file_obj:
            auth_data = json.load(file_obj)

    auth_header = {
        "Authorization": f"Bearer {auth_data['access_token']}"
    }
    server_host = server_conf['host']
    logger.debug(f"Request payload: {payload}")
    if api is FiatBackendRequest.EnvdCreate or api is FiatBackendRequest.DFSCreate:
        serialized_payload = json.dumps(payload)
        resp = requests.post(
            f"{server_host}{api.value}",
            data=serialized_payload,
            headers=auth_header
        )
    else:
        resp = requests.delete(
            f"{server_host}{api.value}",
            params=query,
            headers=auth_header
        )

    if resp.status_code == 422:
        logger.error(f"Validation failed! Reason: {resp.json()}")
        raise Abort()

    logger.debug(f"Complete with response: {resp.json()}")

    return
