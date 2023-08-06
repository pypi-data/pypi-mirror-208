"""
Contains all utility functions
"""
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import json

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class utils:
    def __init__(self, credentials: ClientSecretCredential, authorization_token: str):
        """
        :param credentials:  ClientSecretCredential object
        """
        self.credentials = credentials
        self.authorization_token = authorization_token

    def list_subscriptions(self) -> list:
        """
        :param self:
        :return: list of Azure subscriptions
        """
        logger.info(" ---Inside utils :: list_subscriptions()--- ")

        subs_client = SubscriptionClient(credential=self.credentials)

        subs_list = subs_client.subscriptions.list()
        response = []
        for subs in subs_list:
            sid = subs.id
            response.append(sid.split('/')[-1])

        return response

    def list_vms(self, subscriptions: list) -> dict:
        """
        :param subscriptions: list of subscriptions
        :return: dictionary containing the list VMs
        """
        logger.info(" ---Inside utils :: list_vms()--- ")

        response = {}

        for subscription in subscriptions:
            compute_client = ComputeManagementClient(credential=self.credentials, subscription_id=subscription)
            vm_list = compute_client.virtual_machines.list_all()

            for vm in vm_list:
                response.setdefault(subscription, []).append(vm)

        return response

    # returns the list of disks across all the subscriptions
    def list_disks(self, subscriptions: list) -> dict:
        """
        :param subscriptions: list of subscriptions
        :return:
        """
        logger.info(" ---Inside utils :: list_disks()--- ")
        response = {}

        for subscription in subscriptions:
            compute_client = ComputeManagementClient(credential=self.credentials, subscription_id=subscription)
            disk_lst = compute_client.disks.list()

            for disk in disk_lst:
                response.setdefault(subscription, []).append(disk)

        return response

    # returns the list of snapshots
    def list_snapshots(self, subscriptions: list) -> dict:
        """
        :param subscriptions: list of azure subscriptions
        :return: list of snapshots
        """
        logger.info(" ---Inside utils :: list_snapshots()--- ")
        response = {}

        for subscription in subscriptions:
            compute_client = ComputeManagementClient(credential=self.credentials, subscription_id=subscription)
            snapshot_list = compute_client.snapshots.list()

            for snapshot in snapshot_list:
                response.setdefault(subscription, []).append(snapshot)

        return response

    '''***********************Incomplete'''

    # returns the list of load balancers across all subscriptions
    def list_load_balancers(self, subscriptions: list) -> dict:
        """
        :param subscriptions: list of subscription in an azure account
        :return: dictionary containing list of load balancers
        """
        logger.info(" ---Inside utils :: list_load_balancers()--- ")

        response = {}

        for subscription in subscriptions:
            client = NetworkManagementClient(credential=self.credentials, subscription_id=subscription)
            lb_list = client.load_balancers.list_all()
            for lb in lb_list:
                print(lb)

        return response

    # returns the list of NSG
    def list_nsg(self, subscriptions: list) -> dict:
        """
        :param subscriptions: list of subscriptions
        :return: dictionary containing list of nsg
        """
        logger.info(" ---Inside utils :: list_nsg()--- ")

        response = {}

        for subscription in subscriptions:
            client = NetworkManagementClient(credential=self.credentials, subscription_id=subscription)
            nsg_list = client.network_security_groups.list_all()

            for nsg in nsg_list:
                response.setdefault(subscription, []).append(nsg)

        return response

    # returns the pricing of the particular resource
    def get_price(self, resource, subscription_id: str) -> dict:
        """
        :param subscription_id:
        :param resource:
        :return:
        """
        logger.info(" ---Inside utils :: get_price()--- ")

        # Usage details API
        usage_start = datetime.datetime.now().date().replace(day=1)
        # print(usage_start)
        usage_end = datetime.datetime.now().date()

        url = "https://management.azure.com/subscriptions/{}/providers/Microsoft" \
              ".Consumption/usageDetails?api-version=2019-10-01&$filter=properties/usageStart ge '{}' and " \
              "properties/usageEnd lt '{}'".format(subscription_id, str(usage_start), str(usage_end))
        # print(url)

        # url = "https://management.azure.com/subscriptions/{}/providers/Microsoft.Consumption/usageDetails?api-version=2019-10-01&".format(
        #     subscription_id)
        payload = {}

        headers = {
            'Authorization': 'Bearer ' + self.authorization_token
        }
        meter_id = None
        # print('Resource Id: ' + resource.id)
        while True:
            flag = False
            # print(url)
            response = requests.request("GET", url, headers=headers, data=payload)

            response_json_obj = json.loads(response.text)
            # print(response_json_obj)

            if 'value' in response_json_obj:
                if len(response_json_obj['value']) == 0:
                    logger.info('Resource not found in billing data')
                    return {
                        'unitOfMeasure': None,
                        'retail_price': 0
                    }
            else:
                logger.info('Resource not found in billing data')
                return {
                    'unitOfMeasure': None,
                    'retail_price': 0
                }

            for item in response_json_obj['value']:
                # print(item)
                try:
                    resource_id = item['properties']['resourceId']
                except KeyError as e:
                    return {'unitOfMeasure': None, 'retail_price': 0}

                if resource.id == resource_id:
                    meter_id = item['properties']['meterId']
                    flag = True
                    break
            if flag:
                break
            if 'nextLink' in response_json_obj:
                url = response_json_obj['nextLink']
                if url == '' or url is None:
                    break
            else:
                break

        ################################################################
        if meter_id is None:
            logger.info('Resource not found in billing data')
            return {
                'unitOfMeasure': None,
                'retail_price': 0
            }
        else:
            url = "https://prices.azure.com/api/retail/prices"
            params = {
                '$filter': "meterId eq '{}' and armRegionName eq '{}' and currencyCode eq 'USD'".format(meter_id,
                                                                                                        resource.location),
                '$skip': 0
            }
            payload = {}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload, params=params).text
            json_obj = json.loads(response)

            # print('*******************')
            # print(resource)
            res = {
                'unitOfMeasure': None,
                'retail_price': 0
            }
            for obj in json_obj['Items']:
                if 'reservationTerm' in obj:
                    if obj['reservationTerm'] == '':
                        # print(json.dumps(obj, indent=4))
                        res['unitOfMeasure'] = obj['unitOfMeasure']
                        res['retail_price'] = obj['retailPrice']
                        break
                else:
                    # print(json.dumps(obj, indent=4))
                    res['unitOfMeasure'] = obj['unitOfMeasure']
                    res['retail_price'] = obj['retailPrice']
                    break

            return res

    # returns the list of resource groups
    def list_resource_groups(self, subscriptions: list) -> dict:
        """
        :param subscriptions:
        :return:
        """
        logger.info(" ---Inside utils :: list_resource_groups()--- ")

        rg_list = {}

        for subscription_id in subscriptions:
            url = "https://management.azure.com/subscriptions/{}/resourcegroups?api-version=2021-04-01".format(
                subscription_id)

            payload = {}
            headers = {
                'Authorization': 'Bearer ' + self.authorization_token
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            data = json.loads(response.text)

            if 'value' in data:
                for item in data['value']:
                    rg_list.setdefault(subscription_id, []).append(item['name'])

        return rg_list


def get_rg_name(rid: str):
    data = rid.split('/')
    i = 0
    while i < len(data):
        if data[i].lower() == 'resourcegroups':
            return data[i + 1]
        i += 1
    return None
