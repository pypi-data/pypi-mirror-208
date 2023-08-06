import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from sagemaker_studio_analytics_extension.utils.client_factory import ClientFactory


class TestClientFactory(unittest.TestCase):
    @patch(
        "sagemaker_studio_analytics_extension.utils.client_factory.boto3.session.Session"
    )
    @patch("sagemaker_studio_analytics_extension.utils.client_factory.boto3.client")
    def test_get_regional_sts_client(self, mock_boto_client, mock_boto_session):
        mock_boto_session.return_value = MagicMock(**{"region_name": "region_name"})
        mock_boto_client.return_value = MagicMock()
        _ = ClientFactory.get_regional_sts_client()
        mock_boto_client.assert_called_with(
            "sts",
            endpoint_url="https://sts.region_name.amazonaws.com",
            region_name="region_name",
        )

    @patch("sagemaker_studio_analytics_extension.utils.client_factory.boto3.client")
    @patch(
        "sagemaker_studio_analytics_extension.utils.client_factory.RegionalClient.get_sts_client"
    )
    def test_get_global_sts_client(
        self, mock_regionalclient_getstsclient, mock_boto_client
    ):
        mock_regionalclient_getstsclient.side_effect = RuntimeError(
            "RuntimeError on initiating regional call"
        )
        mock_boto_client.return_value = MagicMock()
        _ = ClientFactory.get_regional_sts_client()
        mock_boto_client.assert_called_with("sts")
