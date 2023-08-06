# VMware Idem Plugin
# Copyright (c) 2020-2022 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from os import environ
from typing import Any
from typing import Dict

try:
    from google.oauth2.service_account import Credentials as Oauth2Credentials

    import google.auth._service_account_info as service_account_info

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def gather(hub) -> Dict[str, Any]:
    """
    Sets the default profile from the environment. All information can
    be obtained from a standard GCP credentials JSON file. The variables
    required are:

        GCP_AUTH_CLIENT_EMAIL: The service account client e-mail address.
        GCP_AUTH_PRIVATE_KEY_ID: The service account private key id.
        GCP_AUTH_PRIVATE_KEY: The service account private key.
        GCP_AUTH_PROJECT_ID: The id of the project in which the service account.
        GCP_AUTH_TOKEN_URI: The service account token URI.

    Note: The credential type is always "service_account".
    """
    sub_profiles = {}
    credentials = {}
    profile_name = "default"

    creds = {}
    try:
        creds["type"] = "service_account"
        creds["project_id"] = environ["GCP_AUTH_PROJECT_ID"]
        creds["private_key_id"] = environ["GCP_AUTH_PRIVATE_KEY_ID"]
        creds["client_email"] = environ["GCP_AUTH_CLIENT_EMAIL"]
        creds["private_key"] = environ["GCP_AUTH_PRIVATE_KEY"]
        creds["token_uri"] = environ["GCP_AUTH_TOKEN_URI"]
    except KeyError:
        return {}

    signer = service_account_info.from_dict(
        creds, require=["client_email", "token_uri"]
    )
    credentials = Oauth2Credentials(
        signer,
        service_account_email=creds["client_email"],
        token_uri=creds["token_uri"],
        project_id=creds["project_id"],
    )
    sub_profiles[profile_name] = {"credentials": credentials}

    return sub_profiles
