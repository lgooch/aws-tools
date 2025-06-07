#!/usr/bin/env python3

"""Tool to delete default VPCs in all regions."""

import argparse
import boto3


def delete_subnets(ec2, vpcid):
    """
    Deletes all subnets within a specified VPC.

    Args:
        ec2 (boto3.client): The Boto3 EC2 client used to interact with AWS EC2 resources.
        vpcid (str): The ID of the VPC whose subnets will be deleted.

    Note:
        This function will delete all subnets in the specified VPC. Ensure that no resources 
        are dependent on these subnets before deletion.
    """
    subnets = ec2.describe_subnets(
        Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}]
    )['Subnets']
    for subnet in subnets:
        ec2.delete_subnet(SubnetId=subnet['SubnetId'])


def delete_security_groups(ec2, vpcid):
    """
    Deletes all security groups within a specified VPC, except for the default security group.

    Args:
        ec2 (boto3.client): The Boto3 EC2 client used to interact with AWS EC2 resources.
        vpcid (str): The ID of the VPC whose security groups should be deleted.

    Notes:
        - The function skips deletion of the default security group.
        - Assumes that the caller has sufficient permissions to describe and delete security groups.
    """
    sgs = ec2.describe_security_groups(
        Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}]
    )['SecurityGroups']
    for sgp in sgs:
        default = sgp['GroupName']
        if default != 'default':
            sgid = sgp['GroupId']
            ec2.delete_security_group(GroupId=sgid)


def delete_nacls(ec2, vpcid):
    """
    Deletes all non-default network ACLs associated with a specified VPC.

    Args:
        ec2 (boto3.client): The Boto3 EC2 client used to interact with AWS EC2 resources.
        vpcid (str): The ID of the VPC whose non-default network ACLs should be deleted.

    Note:
        Default network ACLs are not deleted.
    """

    nacls = ec2.describe_network_acls(
        Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}]
    )['NetworkAcls']
    for nacl in nacls:
        if nacl["IsDefault"] is not True:
            ec2.delete_network_acl(NetworkAclId=nacl['NetworkAclId'])


def delete_igws(ec2, vpcid):
    """
    Deletes all internet gateways attached to the specified VPC.

    Args:
        ec2 (boto3.client): The Boto3 EC2 client.
        vpcid (str): The ID of the VPC whose internet gateways should be deleted.

    Note:
        This function finds all internet gateways attached to the given VPC,
        detaches them, and then deletes them.
    """
    igws = ec2.describe_internet_gateways(
        Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpcid]}]
    )['InternetGateways']
    for igw in igws:
        ec2.detach_internet_gateway(
            InternetGatewayId=igw['InternetGatewayId'],
            VpcId=vpcid)
        ec2.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])


def delete_dependencies(ec2, vpcid):
    """
    Deletes all dependencies associated with a specified VPC.

    This function removes all subnets, security groups, network ACLs, and internet gateways
    attached to the given VPC. It is typically used as a preparatory step
    before deleting the VPC itself.

    Args:
        ec2: A boto3 EC2 resource or client object used to interact with AWS EC2.
        vpcid (str): The ID of the VPC whose dependencies are to be deleted.
    """
    delete_subnets(ec2, vpcid)
    delete_security_groups(ec2, vpcid)
    delete_nacls(ec2, vpcid)
    delete_igws(ec2, vpcid)


def delete_vpc(ec2, vpcid):
    """
    Deletes the VPC with the specified VPC ID.

    Args:
        ec2 (boto3.client): The Boto3 EC2 client used to perform the deletion.
        vpcid (str): The ID of the VPC to delete.
    """
    ec2.delete_vpc(VpcId=vpcid)


def main():
    """
    Main function to parse command-line arguments and delete default VPCs across all AWS regions.

    This function performs the following steps:
    1. Parses command-line arguments for auto-accepting deletions and specifying an AWS CLI profile.
    2. Initializes a boto3 session and retrieves all available AWS regions.
    3. Iterates through each region, identifies default VPCs, and prompts the user for deletion
    (unless auto-accept is enabled).
    4. Deletes dependencies and the default VPC if confirmed by the user or if auto-accept
    is specified.
    5. Skips non-default VPCs and provides informative output for each action taken.

    Args:
        None. Arguments are parsed from the command line.

    Returns:
        None. The function performs actions and prints output to the console.
    """
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
                    delete_dependencies(ec2, vpc["VpcId"])
                    print("Deleting VPC " + vpc["VpcId"]
                          + " in the region " + region["RegionName"])
                    delete_vpc(ec2, vpc["VpcId"])
                else:
                    response = input("Would you like to delete "
                                     + vpc["VpcId"] + " in the region "
                                     + region["RegionName"] + "? "
                                     + "Type y or n: ").lower().strip()
                    if response in ['y', 'yes']:
                        print("Deleting VPC dependencies for "
                          + vpc["VpcId"] + " in the region "
                          + region["RegionName"])
                        delete_dependencies(ec2, vpc["VpcId"])
                        print("Deleting VPC " + vpc["VpcId"]
                            + " in the region " + region["RegionName"])
                        delete_vpc(ec2, vpc["VpcId"])
                    elif response in ['n', 'no']:
                        print("Skipping deletion of VPC "
                              + vpc["VpcId"] + " in the region "
                              + region["RegionName"])
                    else:
                        print("Invalid response.")
                        return False
            else:
                print("Skipping non-default VPC "
                      + vpc["VpcId"] + " in the region "
                      + region["RegionName"])


if __name__ == '__main__':
    main()
