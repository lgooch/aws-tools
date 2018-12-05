#!/usr/bin/env python3

import boto3

def deleteSubnets(ec2):
    subnets = ec2.describe_subnets()['Subnets']
    for subnet in subnets:
        ec2.delete_subnet(SubnetId=subnet['SubnetId'])

def deleteSecurityGroups(ec2):
    sgs = ec2.describe_security_groups()['SecurityGroups']
    for sgp in sgs:
        default = sgp['GroupName']
        if default != 'default':
            sgid = sgp['GroupId']
            ec2.delete_security_group(GroupId=sgid)

def deleteNACLS(ec2):
    nacls = ec2.describe_network_acls()['NetworkAcls']
    for nacl in nacls:
        if nacl["IsDefault"] != True:
            ec2.delete_network_acl(NetworkAclId=nacl['NetworkAclId'])

def deleteIGWS(ec2, vpcid):
    igws = ec2.describe_internet_gateways()['InternetGateways']
    for igw in igws:
        ec2.detach_internet_gateway(InternetGatewayId=igw['InternetGatewayId'], VpcId=vpcid)
        ec2.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])

# WIP - API doesn't list non associated route tables
# def deleteRouteTables(ec2):
#     rtbs = ec2.describe_route_tables()['RouteTables']
#     for rtb in rtbs:
#         ec2.delete_route_table(RouteTableId=rtb['RouteTableId'])

def deleteVPC(ec2, vpcid):
    ec2.delete_vpc(VpcId=vpcid)

def main():
    client = boto3.client('ec2')

    regions = client.describe_regions()
    for region in regions['Regions']:
        ec2 = boto3.client('ec2',region_name=region["RegionName"])
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs["Vpcs"]:
            if vpc["IsDefault"] == True:
                response = input("Would you like to delete " + vpc["VpcId"] + " in the region " + region["RegionName"] + "? " + "Type y or n (default no): ")
                if response == "y":
                    print("Deleting VPC dependencies")
                    deleteSubnets(ec2)
                    deleteSecurityGroups(ec2)
                    deleteNACLS(ec2)
                    deleteIGWS(ec2,vpc["VpcId"])
                    #deleteRouteTables(ec2)
                    print("Deleting VPC")
                    deleteVPC(ec2,vpc["VpcId"])

if __name__ == '__main__':
    main()
