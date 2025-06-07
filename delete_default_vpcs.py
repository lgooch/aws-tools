#!/usr/bin/env python3

"""Tool to delete default VPCs in all regions."""

import argparse
import boto3


def deletesubnets(ec2):
    """Delete all subnets in the VPC."""
    subnets = ec2.describe_subnets()['Subnets']
    for subnet in subnets:
        ec2.delete_subnet(SubnetId=subnet['SubnetId'])


def deletesecuritygroups(ec2):
    """Delete all security groups in the VPC except the default one."""
    sgs = ec2.describe_security_groups()['SecurityGroups']
    for sgp in sgs:
        default = sgp['GroupName']
        if default != 'default':
            sgid = sgp['GroupId']
            ec2.delete_security_group(GroupId=sgid)


def deletenacls(ec2):
    """Delete all network ACLs in the VPC except the default one."""
    nacls = ec2.describe_network_acls()['NetworkAcls']
    for nacl in nacls:
        if nacl["IsDefault"] is not True:
            ec2.delete_network_acl(NetworkAclId=nacl['NetworkAclId'])


def deleteigws(ec2, vpcid):
    """Delete all internet gateways in the VPC."""
    igws = ec2.describe_internet_gateways()['InternetGateways']
    for igw in igws:
        ec2.detach_internet_gateway(
            InternetGatewayId=igw['InternetGatewayId'],
            VpcId=vpcid)
        ec2.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])


def deletevpc(ec2, vpcid):
    """Delete the VPC."""
    ec2.delete_vpc(VpcId=vpcid)


def main():
    """Main function to parse arguments and delete default VPCs."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auto-accept', action='store_true',
                        help="Auto accept the deletion of the VPC's")
    parser.add_argument('-p', '--profile',
                        help="The aws cli profile to use")
    arg = parser.parse_args()

    session = boto3.Session(profile_name=arg.profile)
    client = session.client('ec2')
    regions = client.describe_regions()

    for region in regions['Regions']:
        ec2 = session.client('ec2', region_name=region["RegionName"])
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs["Vpcs"]:
            if vpc["IsDefault"] is True:
                if arg.auto_accept:
                    print("Deleting VPC dependencies for "
                          + vpc["VpcId"] + " in the region "
                          + region["RegionName"])
                    deletesubnets(ec2)
                    deletesecuritygroups(ec2)
                    deletenacls(ec2)
                    deleteigws(ec2, vpc["VpcId"])
                    print("Deleting VPC " + vpc["VpcId"]
                          + " in the region " + region["RegionName"])
                    deletevpc(ec2, vpc["VpcId"])
                else:
                    response = input("Would you like to delete "
                                     + vpc["VpcId"] + " in the region "
                                     + region["RegionName"] + "? "
                                     + "Type y or n: ").lower().strip()
                    if response in ['y', 'yes']:
                        print("Deleting VPC dependencies")
                        deletesubnets(ec2)
                        deletesecuritygroups(ec2)
                        deletenacls(ec2)
                        deleteigws(ec2, vpc["VpcId"])
                        print("Deleting VPC")
                        deletevpc(ec2, vpc["VpcId"])
                    elif response in ['n', 'no']:
                        print("Skipping deletion of VPC "
                              + vpc["VpcId"] + " in the region "
                              + region["RegionName"])
                    else:
                        print("Invalid response. Please type y or n.")


if __name__ == '__main__':
    main()
