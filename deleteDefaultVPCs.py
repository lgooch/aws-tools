#!/usr/bin/env python3

import boto3
import argparse

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

def deleteVPC(ec2, vpcid):
    ec2.delete_vpc(VpcId=vpcid)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--accept', default="n",
                        help="Auto accept the deletion of the VPC's. Valid values are y or n")
    parser.add_argument('-p', '--profile',
                        help="The aws cli profile to use")
    arg = parser.parse_args()

    session = boto3.Session(profile_name=arg.profile)
    client = session.client('ec2')
    regions = client.describe_regions()
    
    for region in regions['Regions']:
        ec2 = session.client('ec2',region_name=region["RegionName"])
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs["Vpcs"]:
            if vpc["IsDefault"] == True:
                if arg.accept == "y":
                    print("Deleting VPC dependencies for " + vpc["VpcId"] + " in the region " + region["RegionName"])
                    deleteSubnets(ec2)
                    deleteSecurityGroups(ec2)
                    deleteNACLS(ec2)
                    deleteIGWS(ec2,vpc["VpcId"])
                    print("Deleting VPC "  + vpc["VpcId"] + " in the region " + region["RegionName"])
                    deleteVPC(ec2,vpc["VpcId"])
                elif arg.accept == "n":
                    response = input("Would you like to delete " + vpc["VpcId"] + " in the region " + region["RegionName"] + "? " + "Type y or n (default no): ")
                    if response == "y":
                        print("Deleting VPC dependencies")
                        deleteSubnets(ec2)
                        deleteSecurityGroups(ec2)
                        deleteNACLS(ec2)
                        deleteIGWS(ec2,vpc["VpcId"])
                        print("Deleting VPC")
                        deleteVPC(ec2,vpc["VpcId"])

if __name__ == '__main__':
    main()
