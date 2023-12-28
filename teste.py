#import json
#import sys
#import time
import boto3

## Imports libraries created by us. ##
from creating_aws_objects import create_keypair, create_security_group, create_instances, create_instance_profiles
#from cleaning import main as cleaning_after_tests
#from workloads import run_workloads

def main():
    ## The 'client' variable creates a link to the EC2 service. ##
    ##iam_client = boto3.client('iam')

    # Replace 'your_instance_id' and 'your_command' with your actual values
    instance_id = 'i-02578f18af0decc31'
    command = 'apt-get update'  # Replace with the command you want to execute
    #### IDK IF THIS NEEDS SUDO OR NOT. PLS CHECK

    # Create an SSM client
    ssm_client = boto3.client('ssm')

    # Send the command to the EC2 instance
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command]}
    )

    # Get the command ID for later retrieval
    command_id = response['Command']['CommandId']

    # Print the command ID
    print(f"Command ID: {command_id}")

    # Wait for the command to complete
    waiter = ssm_client.get_waiter('command_executed')
    waiter.wait(CommandId=command_id, InstanceId=instance_id)

    # Get the command output
    output = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id
    )['StandardOutputContent']

    # Print the command output
    print(f'Command Output:\n{output}')


##  Takes the program back to main(). ##
if __name__ == '__main__':
    main()
