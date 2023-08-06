from azure.identity import ClientSecretCredential

from azure_recommendations.recommendation import recommendation

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

__author__ = 'Dheeraj Banodha'
__version__ = '0.3.3'


class az_session(recommendation):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        :param tenant_id: tenant Id from Azure
        :param client_id: Access ID
        :param client_secret: Secret Access ID
        """
        super().__init__(tenant_id, client_id, client_secret)
