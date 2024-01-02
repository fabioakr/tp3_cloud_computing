""" 
    This is the main file for TP2, for the Advanced Cloud Computing course. 
"""

## Imports libraries publicly available. ##
import json
#import sys
import time
import boto3

## Imports libraries created by us. ##
from creating_aws_objects import create_keypair, create_security_group
from creating_aws_objects import create_instances, create_instance_profiles
from cleaning import main as cleaning_after_tests
#from workloads import run_workloads

def main():
    ## Assigns region name to be used.
    region_name = 'us-east-1'

    ## Assigns key pair name to be used.
    key_pair_name = 'key_pair_tp3'

    ## The 'client' variable creates a link to the EC2 service. ##
    client = boto3.client('ec2', region_name)

    ## EC2 client. ##
    ec2 = boto3.resource('ec2', region_name)

    ## IAM client. ##
    iam_client = boto3.client('iam')

    ## SSM client. ##
    ssm_client = boto3.client('ssm', region_name=region_name)

    ## Create keypair if it doesn't exist yet. ##
    print()
    key_pair = create_keypair(client, key_pair_name)

    ## Create security group if it doesn't exist yet. ##
    security_id_workers = create_security_group(client, 'security_group_workers', [22, 8000, 8001])

    ## Create instance profile if it doesn't exist yet. ##
    print()
    instance_profile_arn = create_instance_profiles(iam_client)

    ## Create instances. ##
    print()
    workers = create_instances(ec2,
                                1,
                                't2.micro',
                                'ami-053b0d53c279acc90',
                                security_id_workers,
                                open('standalone_mysql.sh', 'r').read(),
                                key_pair,
                                'us-east-1a',
                                8,
                                instance_profile_arn)

    ## Collects instance ids. Needed for sending the command  ##
    ## to read the log file containing the benchmark results. ##
    instance_ids = [instance.instance_id for instance in workers]
    instance_id = instance_ids[0]

    ## Puts the code on hold, so instance has enough time to run benchmark. ##
    print('\nPlease wait, while the benchmark is running... This will take a while!\n')
    time.sleep(400)
    ## 60 120 240 300 before

    ## Sends command to read the log file containing the benchmark results. ##
    file_path = '/var/log/bench_results.txt'
    response = ssm_client.send_command(
        InstanceIds=instance_ids,
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [f'cat {file_path}']}
    )

    # Retrieve the command output
    command_id = response['Command']['CommandId']

    # Wait for the command to complete
    waiter = ssm_client.get_waiter('command_executed')
    waiter.wait(
        CommandId=command_id,
        InstanceId=instance_id
    )

    # Get the command output
    output = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id
    )['StandardOutputContent']

    # Print the file contents on the terminal
    print(f'Contents of {file_path}:\n{output}')

    ## Terminates all instances and load balancers to save up AWS credits. ##
    print('Finally, now terminating all instances...\n')
    cleaning_after_tests(client)


##  Takes the program back to main(). ##
if __name__ == '__main__':
    main()
