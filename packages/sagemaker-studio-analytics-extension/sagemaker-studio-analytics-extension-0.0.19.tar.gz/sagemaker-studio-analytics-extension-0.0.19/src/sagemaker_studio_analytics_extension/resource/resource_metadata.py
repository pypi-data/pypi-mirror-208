import pkg_resources

from ..utils.constants import EXTENSION_NAME
from ..utils.client_factory import ClientFactory


class ResourceMetadata:
    def __init__(self):
        try:
            self.library_version = pkg_resources.get_distribution(
                EXTENSION_NAME
            ).version
        except Exception as e:
            self.library_version = "UNKNOWN"

        self.sts_client = ClientFactory.get_regional_sts_client()
        self.account_id = self.sts_client.get_caller_identity().get("Account")
