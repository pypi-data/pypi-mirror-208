import logging

from azure.identity import ClientSecretCredential
from azure.mgmt.advisor import AdvisorManagementClient
from azure.mgmt.compute import ComputeManagementClient

from azure_recommendations.recommendation import utils
from azure_recommendations.recommendation.utils import get_rg_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class advisor_recommendations:
    def __init__(self, credentials: ClientSecretCredential, authorization_token: str):
        """
        :param credentials: ClientSecretCredential
        """
        self.credentials = credentials
        self.authorization_token = authorization_token

    # Provides the recommendation from Azure advisor
    def azure_advisor_recommendations(self, subscription_list: list) -> list:
        """
        :param subscription_list: list of azure subscriptions
        :return: list of recommendations
        """
        logger.info(" ---Inside advisor_recommendations :: azure_advisor_recommendations()--- ")

        response = []
        recommendation_to_consider = [
            'Right-size or shutdown underutilized virtual machines'
        ]

        utils_obj = utils(self.credentials, self.authorization_token)

        vm_list = utils_obj.list_vms(subscriptions=subscription_list)

        for subscription in subscription_list:
            advisor_client = AdvisorManagementClient(credential=self.credentials, subscription_id=subscription)

            recommendation_list = advisor_client.recommendations.list()
            temp = {}
            # print(len(recommendation_list))
            for recommendation in recommendation_list:
                if recommendation.short_description.solution == 'You have disks which have not been attached to a VM for more than 30 days. Please evaluate if you still need the disk.':
                    continue

                if recommendation.resource_metadata.resource_id not in temp:
                    temp[recommendation.resource_metadata.resource_id] = []
                if recommendation.short_description.solution not in temp[recommendation.resource_metadata.resource_id]:
                    # print(recommendation.short_description)
                    # print(recommendation.resource_metadata)
                    # print(recommendation)
                    current_price = 0
                    if recommendation.short_description.solution in recommendation_to_consider:
                        # print('***********************1')
                        for vm in vm_list[subscription]:
                            if str(vm.id).lower() == str(recommendation.resource_metadata.resource_id).lower():
                                # print('*******************************3')
                                prices = utils_obj.get_price(subscription_id=subscription, resource=vm)
                                if prices['unitOfMeasure'] == '1 Hour':
                                    # print(prices)
                                    current_price = 730 * prices['retail_price']

                    effective_price = 0
                    savings = current_price - effective_price
                    try:
                        savings_p = ((current_price - effective_price) / current_price) * 100
                    except ZeroDivisionError:
                        savings_p = 0
                    temp = {
                        'recommendation': recommendation.short_description.solution,
                        'Category': recommendation.category,
                        'description': recommendation.short_description.solution,
                        'resource group': get_rg_name(recommendation.resource_metadata.resource_id),
                        'resource name': str(recommendation.resource_metadata.resource_id).split('/')[-1],
                        'resource': recommendation.resource_metadata.resource_id.split('/')[-2],
                        'subscription_id': subscription,
                        'resource_id': recommendation.resource_metadata.resource_id,
                        'metadata': {},
                        'current cost': current_price,
                        'effective cost': effective_price,
                        'savings': savings,
                        'savings %': savings_p,
                        'source': 'Azure'
                    }
                    temp.setdefault(recommendation.resource_metadata.resource_id, []).append(recommendation.short_description.solution)
                    response.append(temp)
                # print(recommendation.category)
                # print(recommendation.short_description.solution)
                # print(recommendation.resource_metadata)

        return response
