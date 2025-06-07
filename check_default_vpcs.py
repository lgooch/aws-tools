#!/usr/bin/env python3

"""Checks whether the default VPC is in use across all regions."""

import argparse
import boto3


def check_for_enis(ec2, vpcid):
    """
    Checks if there are any Elastic Network Interfaces (ENIs) associated with the specified VPC.

    Args:
        ec2 (boto3.client): The Boto3 EC2 client used to interact with AWS EC2 resources.
        vpcid (str): The ID of the VPC to check for ENIs.

    Returns:
        bool: True if there are ENIs associated with the VPC, False otherwise.
    """
    enis = ec2.describe_network_interfaces(
        Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}]
    )['NetworkInterfaces']
    return len(enis) > 0


def main():
    """
    Checks all AWS regions for default VPCs using the specified AWS CLI profile,
    and reports whether each default VPC is in use.

    Args:
      -p, --profile (str): The AWS CLI profile name to use for authentication.

    Behavior:
      - Iterates through all AWS regions.
      - For each region, finds default VPCs.
      - Checks if each default VPC is in use by calling `check_for_enis`.
      - Prints the usage status of each default VPC.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--profile',
                        help="The aws cli profile to use")
    arg = parser.parse_args()

    session = boto3.Session(profile_name=arg.profile)
    client = session.client('ec2')
    regions = client.describe_regions()['Regions']

    for region in regions:
        ec2 = session.client('ec2', region_name=region["RegionName"])
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs["Vpcs"]:
            if vpc["IsDefault"] is True:
                vpcid = vpc["VpcId"]
                if check_for_enis(ec2, vpcid):
                    print(f"Default VPC {vpcid} is in use in region {region['RegionName']}.")
                else:
                    print(f"Default VPC {vpcid} is not in use in region {region['RegionName']}.")

if __name__ == "__main__":
    main()
