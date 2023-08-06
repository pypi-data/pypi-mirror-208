# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from enum import Enum

LIBRARY_NAME = "sagemaker-analytics"
EXTENSION_NAME = "sagemaker_studio_analytics_extension"


class SERVICE(str, Enum):
    EMR = "emr"

    @staticmethod
    def list():
        return list(map(lambda s: s.value, SERVICE))


class OPERATION(str, Enum):
    CONNECT = "connect"

    @staticmethod
    def list():
        return list(map(lambda s: s.value, OPERATION))


## Logging
SAGEMAKER_ANALYTICS_LOG_BASE_DIRECTORY = "/var/log/studio/sagemaker_analytics"

## Auth Types For Logging
AUTH_TYPE_LDAP_FOR_LOGGING = "ldap"
AUTH_TYPE_KERBEROS_FOR_LOGGING = "kerberos"
AUTH_TYPE_HTTP_BASIC_FOR_LOGGING = "http-basic"
AUTH_TYPE_RBAC_FOR_LOGGING = "rbac"
AUTH_TYPE_NO_AUTH_FOR_LOGGING = "no-auth"
AUTH_TYPE_SET_FOR_LOGGING = (
    AUTH_TYPE_LDAP_FOR_LOGGING,
    AUTH_TYPE_KERBEROS_FOR_LOGGING,
    AUTH_TYPE_HTTP_BASIC_FOR_LOGGING,
    AUTH_TYPE_RBAC_FOR_LOGGING,
    AUTH_TYPE_NO_AUTH_FOR_LOGGING,
)


class VerifyCertificateArgument:
    class VerifyCertificateArgumentType(str, Enum):
        """
        TRUE is same as verifying with public CA Cert
        """

        PUBLIC_CA_CERT = "True"
        IGNORE_CERT_VERIFICATION = "False"
        PATH_TO_CERT = "PathToCert"

        @staticmethod
        def list():
            return list(
                map(
                    lambda s: s.value,
                    VerifyCertificateArgument.VerifyCertificateArgumentType,
                )
            )

    def __init__(self, verify_certificate: str):
        self.value = None
        if verify_certificate.lower() == "true":
            self.type = self.VerifyCertificateArgumentType.PUBLIC_CA_CERT
            self.value = True
        elif verify_certificate.lower() == "false":
            self.type = self.VerifyCertificateArgumentType.IGNORE_CERT_VERIFICATION
            self.value = False
        else:
            self.type = self.VerifyCertificateArgumentType.PATH_TO_CERT
            self.value = verify_certificate
