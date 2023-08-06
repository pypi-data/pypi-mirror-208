import json
from datetime import datetime, timedelta
import re
import pytz
import requests
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure_recommendations.recommendation.utils import get_rg_name

import logging

from azure_recommendations.recommendation import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class vm_recommendations:
    def __init__(self, credentials: ClientSecretCredential, authorization_token: str):
        """
        :param credentials: ClientSecretCredential
        """
        super().__init__(credentials)
        self.credentials = credentials
        self.authorization_token = authorization_token

    # provides the recommendation to use ssh authentication type
    def check_for_ssh_authentication_type(self, vm_list: dict) -> list:
        """
        :param vm_list: list of the virtual machine across all the subscriptions
        :return: list of recommendations
        """
        logger.info(" ---Inside vm_recommendations :: disk_encryption_for_boot_disk_volumes()--- ")

        response = []

        for subs, vms in vm_list.items():
            for vm in vms:
                # print(vm)
                # print(vm.storage_profile.os_disk)
                # print(vm.storage_profile.os_disk.managed_disk)
                try:
                    if vm.os_profile.linux_configuration is not None:
                        if not vm.os_profile.linux_configuration.disable_password_authentication:
                            temp = {
                                'recommendation': 'Use SSH authentication type',
                                'Category': 'Operational Best Practice',
                                'description': 'the SSH authentication type for the selected Microsoft Azure '
                                               'virtual machine is password-based, therefore the SSH authentication '
                                               'method configured for the specified VM is not secure',
                                'resource': 'Virtual Machine',
                                'resource group': get_rg_name(vm.id),
                                'resource name': str(vm.id).split('/')[-1],
                                'subscription_id': subs,
                                'resource_id': vm.id,
                                'metadata': {
                                    'name': vm.name,
                                    'tags': vm.tags,
                                    'region': vm.location
                                },
                                'current cost': 0,
                                'effective cost': 0,
                                'savings': 0,
                                'savings %': 0,
                                'source': 'Klera'
                            }
                            response.append(temp)
                except AttributeError:
                    continue

        return response

    # Provides recommendations for removing unattached virtual machine disk volumes
    def remove_unattached_disk_volume(self, disk_list: dict) -> list:
        """
        :param disk_list: list of disks across all the subscriptions
        :return: list of recommendations
        """
        logger.info(" ---Inside vm_recommendations :: remove_unattached_disk_volumes()--- ")

        utils_obj = utils(self.credentials, self.authorization_token)
        response = []

        for subscription, disks in disk_list.items():
            for disk in disks:
                # print(disk)
                if disk.disk_state == 'Unattached':
                    prices = utils_obj.get_price(subscription_id=subscription, resource=disk)
                    # print('*******************')
                    # print(prices)
                    current_price = 0
                    if prices['unitOfMeasure'] == '1 GB':
                        current_price = disk.disk_size_gb * prices['retail_price']
                    elif prices['unitOfMeasure'] == '1/Month':
                        current_price = prices['retail_price']

                    effective_price = 0
                    savings = current_price - effective_price
                    try:
                        savings_p = ((current_price - effective_price) / current_price) * 100
                    except ZeroDivisionError:
                        savings_p = 0

                    temp = {
                        'recommendation': 'Remove unattached disk',
                        'Category': 'Cost',
                        'description': 'disk volume is not attached to a Microsoft Azure virtual machine, remove it to optimize the cost',
                        'resource group': get_rg_name(disk.id),
                        'resource name': str(disk.id).split('/')[-1],
                        'resource': 'Virtual Machine',
                        'subscription_id': subscription,
                        'resource_id': disk.id,
                        'metadata': {
                            'name': disk.name,
                            'tags': disk.tags,
                            'region': disk.location
                        },
                        'current cost': current_price,
                        'effective cost': effective_price,
                        'savings': savings,
                        'savings %': savings_p,
                        'source': 'Klera'
                    }
                    response.append(temp)

        return response

    # Provides the recommendation for Remove Old Virtual Machine Disk Snapshots
    def remove_old_vm_disk_snapshot(self, snapshot_list: dict) -> list:
        """
        :param snapshot_list: list of snapshots across all subscriptions
        :return: list of recommendations
        """
        logger.info(" ---Inside vm_recommendations :: remove_old_vm_disk_snapshot()--- ")

        response = []
        utils_obj = utils(self.credentials, self.authorization_token)

        time_30_days_ago = datetime.now() - timedelta(days=30)
        timezone = pytz.timezone("UTC")
        time_30_days_ago = timezone.localize(time_30_days_ago)

        for subscription, snapshots in snapshot_list.items():
            for snapshot in snapshots:
                time_created = snapshot.time_created
                if time_30_days_ago > time_created:
                    prices = utils_obj.get_price(subscription_id=subscription, resource=snapshot)
                    # print(prices)
                    current_price = 0
                    if prices['unitOfMeasure'] == '1 GB/Month':
                        current_price = snapshot.disk_size_gb * prices['retail_price']

                    effective_price = 0
                    savings = current_price - effective_price
                    try:
                        savings_p = ((current_price - effective_price) / current_price) * 100
                    except ZeroDivisionError:
                        savings_p = 0

                    temp = {
                        'recommendation': 'Remove 30 days older vm disk snapshot',
                        'Category': 'Cost',
                        'description': 'virtual machine disk snapshot is 30 days old and can be safely removed '
                                       'from your Azure cloud account',
                        'resource': 'Virtual Machine',
                        'subscription_id': subscription,
                        'resource group': get_rg_name(snapshot.id),
                        'resource name': str(snapshot.id).split('/')[-1],
                        'resource_id': snapshot.id,
                        'metadata': {
                            'name': snapshot.name,
                            'tags': snapshot.tags,
                            'region': snapshot.location
                        },
                        'current cost': current_price,
                        'effective cost': effective_price,
                        'savings': savings,
                        'savings %': savings_p,
                        'source': 'Klera'
                    }
                    response.append(temp)

        return response

    # Provides the recommendation for disable premium ssd
    def disable_premium_ssd(self, vm_list: dict) -> list:
        """
        :param vm_list: list of Azure Virtual Machines
        :return: list of recommendations
        """
        logger.info(" ---Inside vm_recommendations :: disable_premium_ssd()--- ")

        response = []

        utils_obj = utils(self.credentials, self.authorization_token)

        def get_disk(rid: str):
            url = "https://management.azure.com/{}?api-version=2021-12-01".format(rid)
            headers = {
                'Authorization': 'Bearer ' + self.authorization_token
            }
            payload = {}
            res = requests.request("GET", url, headers=headers, data=payload)
            return json.loads(res.text)

        def get_cost_data(loc: str, product_name: str, sku_name: str):
            if product_name.startswith('Premium '):
                meter_name = sku_name + ' Disk'
            else:
                meter_name = sku_name.replace('LRS', 'Disks')
            # print(meter_name)
            url = "https://prices.azure.com/api/retail/prices?$filter=serviceName eq 'Storage' and priceType eq " \
                  "'Consumption' and serviceFamily eq 'Storage' and productName eq '{}' and armRegionName eq '{}' and " \
                  "skuName eq '{}' and meterName eq '{}'".format(product_name, loc, sku_name, meter_name)
            # print(url)
            headers = {}
            payload = {}
            res = requests.request("GET", url, headers=headers, data=payload)
            return json.loads(res.text)

        for subscription, vms in vm_list.items():
            for vm in vms:
                os_disk_type = vm.storage_profile.os_disk.managed_disk.storage_account_type
                if os_disk_type == 'Premium_LRS':
                    disk_data = get_disk(vm.storage_profile.os_disk.managed_disk.id)

                    price_premium = get_cost_data(vm.location, 'Premium SSD Managed Disks', disk_data['properties']['tier']+' LRS')
                    # print(disk_data['properties']['tier'])
                    # print(price_premium)
                    price_standard = get_cost_data(vm.location, 'Standard SSD Managed Disks', disk_data['properties']['tier'].replace('P', 'E')+' LRS')
                    # print(price_standard)

                    current_price = price_premium['Items'][0]['retailPrice']
                    effective_price = price_standard['Items'][0]['retailPrice']
                    savings = current_price - effective_price
                    savings_p = (savings / current_price ) * 100

                    temp = {
                        'recommendation': 'Disable premium SSD',
                        'Category': 'Cost',
                        'description': 'Microsoft Azure virtual machines (VMs) are using Premium SSD '
                                       'volumes, use Standard SSD disk volumes for cost-effective storage '
                                       'that fits a broad range of workloads',
                        'resource': 'Virtual Machine',
                        'subscription_id': subscription,
                        'resource group': get_rg_name(vm.id),
                        'resource name': str(vm.id).split('/')[-1],
                        'resource_id': vm.id,
                        'metadata': {
                            'name': vm.name,
                            'tags': vm.tags,
                            'region': vm.location
                        },
                        'current cost': current_price,
                        'effective cost': effective_price,
                        'savings': savings,
                        'savings %': savings_p,
                        'source': 'Klera'
                    }
                    response.append(temp)
                # try:
                #     data_disk_type = vm.storage_profile.data_disks.managed_disk.storage_account_type
                #     if os_disk_type == 'Premium_LRS' or data_disk_type == 'Premium_LRS':
                #         disk_data = get_disk(subscription, vm.storage_profile.data_disks.managed_disk.id)
                #         print(vm.storage_profile.data_disks.managed_disk)
                #         temp = {
                #             'recommendation': 'Disable premium SSD',
                #             'Category': 'Cost',
                #             'description': 'Microsoft Azure virtual machines (VMs) are using Premium SSD '
                #                            'volumes, use Standard SSD disk volumes for cost-effective storage '
                #                            'that fits a broad range of workloads',
                #             'resource': 'Virtual Machine',
                #             'subscription_id': subscription,
                #             'resource_id': vm.id,
                #             'metadata': {
                #                 'name': vm.name,
                #                 'tags': vm.tags
                #             },
                #             'current cost': 0,
                #             'effective cost': 0,
                #             'savings': 0,
                #             'savings %': 0,
                #             'source': 'Klera'
                #         }
                #         response.append(temp)
                # except AttributeError:
                #     if os_disk_type == 'Premium_LRS':
                #         temp = {
                #             'recommendation': 'Disable premium SSD',
                #             'Category': 'Cost',
                #             'description': 'Microsoft Azure virtual machines (VMs) are using Premium SSD '
                #                            'volumes, use Standard SSD disk volumes for cost-effective storage '
                #                            'that fits a broad range of workloads',
                #             'resource': 'Virtual Machine',
                #             'subscription_id': subscription,
                #             'resource_id': vm.id,
                #             'metadata': {
                #                 'name': vm.name,
                #                 'tags': vm.tags
                #             },
                #             'current cost': 0,
                #             'effective cost': 0,
                #             'savings': 0,
                #             'savings %': 0,
                #             'source': 'Klera'
                #         }
                #         response.append(temp)

        return response

    # Provides the recommendation for enable auto-shutdown
    def enable_auto_shutdown(self, vm_list: dict) -> list:
        """
        :param vm_list: list of azure virtual machines
        :return: list of recommendation
        """
        logger.info(" ---vm_recommendations :: enable_auto_shutdown()--- ")

        response = []
        utils_obj = utils(self.credentials, self.authorization_token)

        for subscription, vms in vm_list.items():
            resource_client = ResourceManagementClient(credential=self.credentials, subscription_id=subscription)
            for vm in vms:
                auto_shutdown_status = resource_client.resources.get_by_id(vm.id, '2022-11-01'). \
                    properties.get('autoShutdownSettings')
                if auto_shutdown_status is None or auto_shutdown_status == 'Disabled':
                    price = utils_obj.get_price(vm, subscription_id=subscription)
                    print(price)
                    current_price = 0
                    if price['unitOfMeasure'] == '1 Hour':
                        current_price = 730 * price['retail_price']

                    effective_price = current_price * 0.6666
                    savings = current_price - effective_price

                    try:
                        savings_p = ((current_price - effective_price) / current_price) * 100
                    except ZeroDivisionError:
                        savings_p = 0

                    temp = {
                        'recommendation': 'Enable Auto Shutdown',
                        'Category': 'Cost',
                        'description': 'Enable Auto Shutdown feature on Microsoft Azure virtual machines (VMs) in '
                                       'order to minimize waste and control VM costs. Assuming the VMs are shut down for 8 hours a day',
                        'resource': 'Virtual Machine',
                        'resource group': get_rg_name(vm.id),
                        'resource name': str(vm.id).split('/')[-1],
                        'subscription_id': subscription,
                        'resource_id': vm.id,
                        'metadata': {
                            'name': vm.name,
                            'tags': vm.tags,
                            'region': vm.location
                        },
                        'current cost': current_price,
                        'effective cost': effective_price,
                        'savings': savings,
                        'savings %': savings_p,
                        'source': 'Klera'
                    }
                    response.append(temp)

        return response

    # Provides the recommendation for unused load balancers
    def unused_load_balancers(self, lb_list: dict) -> list:
        """
        :param lb_list: list of load balancers across all subscriptions
        :return: list of recommendations
        """
        logger.info(" ---Inside vm_recommendation :: unused_load_balancers()--- ")

        response = []

        return response

    # Provides the recommendations for reservations
    def get_reservation_recommendations(self, resource_groups: dict, r_type: str) -> list:
        """
        :param r_type:
        :param resource_groups:
        :return: list of recommendations
        """
        logger.info(" ---Inside vm_recommendations :: get_reservation_recommendations() ---")

        recommendations = []

        for subscription, rg_list in resource_groups.items():
            for rg in rg_list:
                url = "https://management.azure.com//subscriptions/{}/resourceGroups/{}/providers/Microsoft.Consumption/reservationRecommendations?api-version=2021-10-01&$filter=properties/lookBackPeriod eq 'Last60Days' and properties/resourceType eq '{}'".format(subscription, rg, r_type)
                logger.info(url)

                payload = {}
                headers = {
                    'Authorization': 'Bearer '+self.authorization_token
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                data = json.loads(response.text)
                # print(json.dumps(data, indent=2))
                # print(rg)
                # print(json.dumps(data))
                for item in data['value']:
                    lookback_period = item['properties']['lookBackPeriod']

                    current_cost = item['properties']['costWithNoReservedInstances']

                    effective_cost = item['properties']['totalCostWithReservedInstances']

                    # print('current cost')
                    # print(current_cost)
                    # print('effective cost')
                    # print(effective_cost)

                    temp = {
                        'Subscription Id': subscription,
                        'Category': 'Cost',
                        'Resource Type': r_type,
                        'Resource Group': rg,
                        'Number of Instances': item['properties']['recommendedQuantity'],
                        'Current Cost': current_cost,
                        'Effective cost': effective_cost,
                        'Net Savings': current_cost - effective_cost,
                        'Savings %': ((current_cost - effective_cost)/current_cost)*100,
                        'Instance Flexibility Group': item['properties']['instanceFlexibilityGroup'] + ' - ' + item['properties']['normalizedSize'],
                        'location': item['location'],
                        'Term': item['properties']['term'],
                        'source': 'Azure'
                    }
                    recommendations.append(temp)

        return recommendations

