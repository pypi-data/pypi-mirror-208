import logging

from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient

from azure_recommendations.recommendation.utils import get_rg_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class network_recommendations:
    def __init__(self, credentials: ClientSecretCredential, authorization_token: str):
        """
        :param credentials: ClientSecretCredential
        """
        self.credentials = credentials
        self.authorization_token = authorization_token

    # Provides the recommendation for unrestricted CIFS access
    def unrestricted_access(self, nsg_list: dict) -> list:
        """
        :param nsg_list: List of network security groups across all subscriptions
        :return: list of recommendations
        """
        logger.info(" ---Inside network_recommendations :: unrestricted_cifs_access()--- ")

        response = []

        for subscription, items in nsg_list.items():
            for nsg in items:
                # print(nsg.name)
                # print(nsg.id)
                for security_rule in nsg.security_rules:
                    # print(security_rule.protocol)
                    # print(security_rule.destination_port_range)
                    # print(security_rule.access)
                    # print(security_rule.direction)

                    if security_rule.direction == 'Inbound' and security_rule.access == 'Allow' and \
                            security_rule.protocol == 'TCP':
                        destination_port_range = security_rule.destination_port_range
                        if security_rule.source_address_prefix in ["*", "internet", "any"]:
                            recommendation = ""
                            description = ""
                            if destination_port_range == '445':
                                recommendation = "Restrict traffic on TCP port 445"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 445, therefore the CIFS inbound access to " \
                                              "the associated Microsoft Azure virtual machine(s) is not secured"
                            elif destination_port_range == '53':
                                recommendation = "Restrict traffic on TCP port 53"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 53, therefore the DNS inbound access to " \
                                              "the associated Microsoft Azure virtual machine(s) is not secured"
                            elif destination_port_range == '20':
                                recommendation = "Restrict traffic on TCP port 20"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 20, therefore the FTP inbound access to " \
                                              "the associated Microsoft Azure virtual machine(s) is not secured"
                            elif destination_port_range == '21':
                                recommendation = "Restrict traffic on TCP port 21"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 21, therefore the FTP inbound access to " \
                                              "the associated Microsoft Azure virtual machine(s) is not secured"
                            elif destination_port_range == '80':
                                recommendation = "Restrict traffic on TCP port 80"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 80, therefore the HTTP inbound access to " \
                                              "the associated Microsoft Azure virtual machine(s) is not secured"
                            elif destination_port_range == '443':
                                recommendation = "Restrict traffic on TCP port 443"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 443, therefore the HTTPS inbound access to " \
                                              "the associated Microsoft Azure virtual machine(s) is not secured"
                            elif destination_port_range == '1433':
                                recommendation = "Restrict traffic on TCP port 1433"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 1433, therefore the MS SQL Server inbound " \
                                              "access to the associated Microsoft Azure virtual machine(s) is " \
                                              "not secured"
                            elif destination_port_range == '27017':
                                recommendation = "Restrict traffic on TCP port 27017"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 445, therefore the MSSQL Access inbound " \
                                              "access to the associated Microsoft Azure virtual machine(s) is " \
                                              "not secured"
                            elif destination_port_range == '27018':
                                recommendation = "Restrict traffic on TCP port 27018"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 445, therefore the MSSQL Access inbound " \
                                              "access to the associated Microsoft Azure virtual machine(s) is " \
                                              "not secured"
                            elif destination_port_range == '27019':
                                recommendation = "Restrict traffic on TCP port 27019"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 445, therefore the MSSQL Access inbound " \
                                              "access to the associated Microsoft Azure virtual machine(s) is " \
                                              "not secured"
                            elif destination_port_range == '3306':
                                recommendation = "Restrict traffic on TCP port 3306"
                                description = " the selected network security group (NSG) allows unrestricted " \
                                              "traffic on TCP port 445, therefore the MySQL inbound access to " \
                                              "the associated Microsoft Azure virtual machine(s) is not secured"

                            # match destination_port_range:
                            #     case '445':
                            #         recommendation = "Restrict traffic on TCP port 445"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 445, therefore the CIFS inbound access to " \
                            #                       "the associated Microsoft Azure virtual machine(s) is not secured"
                            #
                            #     case '53':
                            #         recommendation = "Restrict traffic on TCP port 53"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 53, therefore the DNS inbound access to " \
                            #                       "the associated Microsoft Azure virtual machine(s) is not secured"
                            #     case '20':
                            #         recommendation = "Restrict traffic on TCP port 20"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 20, therefore the FTP inbound access to " \
                            #                       "the associated Microsoft Azure virtual machine(s) is not secured"
                            #     case '21':
                            #         recommendation = "Restrict traffic on TCP port 21"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 21, therefore the FTP inbound access to " \
                            #                       "the associated Microsoft Azure virtual machine(s) is not secured"
                            #     case '80':
                            #         recommendation = "Restrict traffic on TCP port 80"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 80, therefore the HTTP inbound access to " \
                            #                       "the associated Microsoft Azure virtual machine(s) is not secured"
                            #     case '443':
                            #         recommendation = "Restrict traffic on TCP port 443"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 443, therefore the HTTPS inbound access to " \
                            #                       "the associated Microsoft Azure virtual machine(s) is not secured"
                            #     case '1433':
                            #         recommendation = "Restrict traffic on TCP port 1433"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 1433, therefore the MS SQL Server inbound " \
                            #                       "access to the associated Microsoft Azure virtual machine(s) is " \
                            #                       "not secured"
                            #     case '27017':
                            #         recommendation = "Restrict traffic on TCP port 27017"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 445, therefore the MSSQL Access inbound " \
                            #                       "access to the associated Microsoft Azure virtual machine(s) is " \
                            #                       "not secured"
                            #     case '27018':
                            #         recommendation = "Restrict traffic on TCP port 27018"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 445, therefore the MSSQL Access inbound " \
                            #                       "access to the associated Microsoft Azure virtual machine(s) is " \
                            #                       "not secured"
                            #     case '27019':
                            #         recommendation = "Restrict traffic on TCP port 27019"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 445, therefore the MSSQL Access inbound " \
                            #                       "access to the associated Microsoft Azure virtual machine(s) is " \
                            #                       "not secured"
                            #     case '3306':
                            #         recommendation = "Restrict traffic on TCP port 3306"
                            #         description = " the selected network security group (NSG) allows unrestricted " \
                            #                       "traffic on TCP port 445, therefore the MySQL inbound access to " \
                            #                       "the associated Microsoft Azure virtual machine(s) is not secured"

                            if not recommendation == "":
                                temp = {
                                    'recommendation': recommendation,
                                    'description': description,
                                    'Category': 'Operational Best Practice',
                                    'resource': 'NSG',
                                    'resource group': get_rg_name(nsg.id),
                                    'resource name': str(nsg.id).split('/')[-1],
                                    'subscription_id': subscription,
                                    'resource_id': nsg.id,
                                    'metadata': {
                                        'region': nsg.location
                                    },
                                    'current cost': 0,
                                    'effective cost': 0,
                                    'savings': 0,
                                    'savings %': 0,
                                    'source': 'Klera'
                                }
                                response.append(temp)

        return response
