import json

import requests
from azure.identity import ClientSecretCredential

from azure_recommendations.recommendation.network_recommendations import network_recommendations
from azure_recommendations.recommendation.utils import utils
from azure_recommendations.recommendation.vm_recommendations import vm_recommendations
from azure_recommendations.recommendation.advisor_recommendations import advisor_recommendations

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class recommendation(utils, vm_recommendations, advisor_recommendations, network_recommendations):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        :param tenant_id: tenant Id from Azure
        :param client_id: Access ID
        :param client_secret: Secret Access ID
        """

        self.credentials = ClientSecretCredential(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id
        )
        self.authorization_token = get_token(tenant_id, client_id, client_secret)
        super().__init__(self.credentials, self.authorization_token)

    def get_recommendations(self) -> list:
        """
        :return: list of recommendations
        """
        logger.info(" ---Inside recommendation :: get_recommendations()--- ")

        response = []

        subscriptions = self.list_subscriptions()
        # print('subscriptions')
        # print(subscriptions)

        vm_list = self.list_vms(subscriptions)
        # print(vm_list)
        response.extend(self.check_for_ssh_authentication_type(vm_list))
        response.extend(self.disable_premium_ssd(vm_list))
        response.extend(self.enable_auto_shutdown(vm_list))

        disk_list = self.list_disks(subscriptions)
        # print(disk_list)
        response.extend(self.remove_unattached_disk_volume(disk_list))

        snapshot_list = self.list_snapshots(subscriptions)
        # print(snapshot_list)
        response.extend(self.remove_old_vm_disk_snapshot(snapshot_list))

        response.extend(self.azure_advisor_recommendations(subscriptions))

        nsg_list = self.list_nsg(subscriptions)
        # print(nsg_list)
        response.extend(self.unrestricted_access(nsg_list))

        return response

    def get_reserved_instance_recommendations(self) -> list:
        """
        :return: list of recommendations for the reserved instances
        """
        subscriptions = self.list_subscriptions()
        # print('subscriptions')
        # print(subscriptions)

        response = []

        resource_groups = self.list_resource_groups(subscriptions)

        resource_types = ['VirtualMachines', 'SQLDatabases', 'PostgreSQL', 'ManagedDisk',
                          'MySQL', 'RedHat', 'MariaDB', 'RedisCache', 'CosmosDB', 'SqlDataWarehouse',
                          'SUSELinux', 'AppService', 'BlockBlob', 'AzureDataExplorer', 'VMwareCloudSimple']

        for resource_type in resource_types:
            reservation_recommendations = self.get_reservation_recommendations(resource_groups, r_type=resource_type)
            response.extend(reservation_recommendations)

        return response

    def get_savings_plan_recommendations(self) -> list:
        """
        :return: list of recommendations for savings plan
        """
        subscriptions = self.list_subscriptions()

        recommendations = []
        blacklist_id = []

        for subscription in subscriptions:
            url = "https://management.azure.com/subscriptions/{}/providers/Microsoft.CostManagement/benefitRecommendations?api-version=2022-10-01".format(
                subscription)

            payload = {}

            headers = {
                'Authorization': 'Bearer ' + self.authorization_token
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            json_obj = json.loads(response.text)

            if 'value' in json_obj:
                for item in json_obj['value']:
                    if item['name'] not in blacklist_id:
                        blacklist_id.append(item['name'])
                        temp = {
                            'id': item['id'],
                            'name': item['name'],
                            'averageUtilizationPercentage': item['properties']['recommendationDetails'][
                                'averageUtilizationPercentage'],
                            'coveragePercentage': item['properties']['recommendationDetails']['coveragePercentage'],
                            'commitmentAmount': item['properties']['recommendationDetails']['commitmentAmount'],
                            'overageCost': item['properties']['recommendationDetails']['overageCost'],
                            'benefitCost': item['properties']['recommendationDetails']['benefitCost'],
                            'savingsAmount': item['properties']['recommendationDetails']['savingsAmount'],
                            'savingsPercentage': item['properties']['recommendationDetails']['savingsPercentage'],
                            'totalCost': item['properties']['recommendationDetails']['totalCost'],
                            'wastageCost': item['properties']['recommendationDetails']['wastageCost'],
                            'armSkuName': item['properties']['armSkuName'],
                            'commitmentGranularity': item['properties']['commitmentGranularity'],
                            'currencyCode': item['properties']['currencyCode'],
                            'costWithoutBenefit': item['properties']['costWithoutBenefit'],
                            'firstConsumptionDate': item['properties']['firstConsumptionDate'],
                            'lastConsumptionDate': item['properties']['lastConsumptionDate'],
                            'lookBackPeriod': item['properties']['lookBackPeriod'],
                            'scope': item['properties']['scope'],
                            'term': item['properties']['term'],
                            'totalHours': item['properties']['totalHours'],
                        }
                        recommendations.append(temp)

        return recommendations


def get_token(tenant_id, client_id, client_secret) -> str:
    url = "https://login.microsoftonline.com/{}/oauth2/token".format(tenant_id)

    payload = 'grant_type=client_credentials&client_id={}&client_secret={}&resource=https%3A%2F%2Fmanagement.azure.com%2F'.format(
        client_id, client_secret)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'esctx=PAQABAAEAAAD--DLA3VO7QrddgJg7WevrsyLaTCnWBlfoOEwgEXsbqS6Vk56KJ3f98q4z6wNlD--zONSvPVI_ibZKS8_wcOAqwZYLHwKN1GlMFbChMq1wm9rcpBVNHewxS2ycllzLyDHDniE5l2CFhq88TdEeXS_8JEtBzZT5M2tx9yGb8xOGq4QKBbhOcX6b5Ry-grf0N4yPcxz-dNbt4yri8DshwtoeVuFOeuOvXLRLsk-MVITGzmuMMNbZrNq8JZv_VVzyatwgAA; fpc=Ai2uF3w6uI5OvoKy3lAO3CE6T-WgAQAAAPonotsOAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)

    return data['access_token']
