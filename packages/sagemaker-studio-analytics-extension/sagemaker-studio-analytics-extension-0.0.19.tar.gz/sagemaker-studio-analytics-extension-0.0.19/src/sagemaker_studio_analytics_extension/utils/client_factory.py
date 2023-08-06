import boto3

from .region_constants import DOMAIN, CHINA_DOMAIN, CHINA_REGION_PREFIX
from .client_interface import IClient


class RegionalClient(IClient):
    def __init__(self):
        self.__boto_session = boto3.session.Session()
        self.__region_name = self.__boto_session.region_name
        if self.__region_name.startswith(CHINA_REGION_PREFIX):
            self.regional_sts_endpoint = (
                f"https://sts.{self.__region_name}.{CHINA_DOMAIN}"
            )
        else:
            self.regional_sts_endpoint = f"https://sts.{self.__region_name}.{DOMAIN}"

    def get_sts_client(self):
        return boto3.client(
            "sts",
            endpoint_url=self.regional_sts_endpoint,
            region_name=self.__region_name,
        )


class GlobalClient(IClient):
    def get_sts_client(self):
        return boto3.client("sts")


class ClientFactory:
    @staticmethod
    def get_regional_sts_client():
        try:
            regional_client = RegionalClient()
            sts_client = regional_client.get_sts_client()

        except Exception as e:
            # Fallback on global endpoint
            global_client = GlobalClient()
            sts_client = global_client.get_sts_client()

        return sts_client
