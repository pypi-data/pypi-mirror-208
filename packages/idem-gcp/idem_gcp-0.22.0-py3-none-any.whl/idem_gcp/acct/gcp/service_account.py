# VMware Idem Plugin
# Copyright (c) 2020-2022 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
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


def gather(hub, profiles) -> Dict[str, Any]:
    """
    Get profile names from encrypted service account data

    Example:
    .. code-block:: yaml

        gcp:
          service_account:
            default:
              type: "service_account"
              project_id: "idem_gcp.com:idemgcp"
              private_key_id: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              private_key: "-----BEGIN PRIVATE KEY-----\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxn\n-----END PRIVATE KEY-----\n"
              client_email: "idem-gcp@example.com.iam.gserviceaccount.com"
              client_id: "xxxxxxxxxxxxxxxxxxxxx"
              auth_uri: "https://accounts.google.com/o/oauth2/auth"
              token_uri: "https://oauth2.googleapis.com/token"
              auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"
              client_x509_cert_url: "https://www.googleapis.com/robot/v1/metadata/x509/idem-gcp%40example.com.iam.gserviceaccount.com"
            my-project:
              type: "searvice_account"
              project_id: "idem_gcp.com:my-project"
              private_key_id: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              private_key: "-----BEGIN PRIVATE KEY-----\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxn\n-----END PRIVATE KEY-----\n"
              client_email: "idem-gcp@example.com.iam.gserviceaccount.com"
              client_id: "xxxxxxxxxxxxxxxxxxxxx"
              auth_uri: "https://accounts.google.com/o/oauth2/auth"
              token_uri: "https://oauth2.googleapis.com/token"
              auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"
              client_x509_cert_url: "https://www.googleapis.com/robot/v1/metadata/x509/idem-gcp%40example.com.iam.gserviceaccount.com"
    """
    sub_profiles = {}
    credentials = {}
    for profile, creds in profiles.get("gcp", {}).items():
        signer = service_account_info.from_dict(
            creds, require=["client_email", "token_uri"]
        )
        credentials = Oauth2Credentials(
            signer,
            service_account_email=creds["client_email"],
            token_uri=creds["token_uri"],
            project_id=creds["project_id"],
        )
        sub_profiles[profile] = {"credentials": credentials}

    return sub_profiles
