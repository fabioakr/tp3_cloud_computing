""" 
    This module contains the most important functions made by us to create 
    AWS objects and allow for the necessary operations on TP2. 
"""

import logging
import time
from botocore.exceptions import WaiterError

def create_keypair(client, name):
    """
    Creates a new key pair with the specified name if it doesn't already exist.

    Args:
        client: An instance of the Boto3 EC2 client.
        name: The name of the key pair to create.

    Returns:
        The name of the key pair that was created or already existed.
    """

    print("Checking if the specified key pair name already exists...")

    # Gets all key pairs (if any).
    response = client.describe_key_pairs()

    # Verifies if the key pair already exists.
    # 1st case: there is a key pair with that name already.
    for i in range(0, len(response['KeyPairs'])):
        if response['KeyPairs'][i]["KeyName"] == name:
            print(f"Key pair '{name}' already exists.\n")
            key_pair = response['KeyPairs'][i]
            return key_pair['KeyName']

    # 2nd case: there is no key pair with that name OR there isn't a key pair yet.
    key_pair = client.create_key_pair(KeyName=name)
    print("Key pair doesn't exist, so it was just created.\n")
    return key_pair['KeyName']

def create_security_group(client, name, ports):
    """
    Creates a new security group with the given name and authorizes ingress rules 
    for the specified ports.
    If a security group with the given name already exists, it authorizes ingress
    rules for the specified ports that are not already enabled.

    Args:
        client (boto3.client): The Boto3 client to use.
        name (str): The name of the security group to create or update.
        ports (list): A list of integers representing the ports to authorize ingress rules for.

    Returns:
        str: The ID of the created or updated security group.
    """

    print(f"Checking if '{name}' security group name already exists...")

    # Gets all security groups (if any).
    response = client.describe_security_groups()

    # Verifies if the security group already exists.
    # 1st case: there is a security group with that name already.
    for i in range(0, len(response['SecurityGroups'])):
        if response['SecurityGroups'][i]["GroupName"] == name:
            print(f"Security group '{name}' already exists.")
            security_group = response['SecurityGroups'][i]

            existing_rules = [rule['FromPort'] for rule in security_group['IpPermissions']]

            for port in ports:
                if port not in existing_rules:
                    client.authorize_security_group_ingress(
                        GroupId=security_group['GroupId'],  # Use the security group ID
                        IpPermissions=[
                            {'IpProtocol': 'tcp',
                            'FromPort': port,
                            'ToPort': port,
                            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                        ]
                    )
                    print(f"Inbound port '{port}' enabled in security group '{name}' .")
                else:
                    print(f"Inbound port '{port}' is already enabled in security group '{name}' .")
            return security_group['GroupId']

    # 2nd case: there is no security group with that name OR there isn't a group yet.
    security_group = client.create_security_group(
            GroupName=name,
            Description='TP2 '+name+' Security Group'
    )
    print(f"Security group '{name}' doesn't exist, so it was just created!")

    # Authorize ingress rules using the security group ID

    for port in ports:
        client.authorize_security_group_ingress(
            GroupId=security_group['GroupId'],  # Use the security group ID
            IpPermissions=[
                {'IpProtocol': 'tcp',
                'FromPort': port,
                'ToPort': port,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ]
        )
        print(f"Inbound port '{port}' enabled in security group '{name}' .")
    print()
    return security_group['GroupId']

def create_instance_profiles(iam_client):
    ## Asks for all instance profiles in the account ##
    instance_profile_search = iam_client.list_instance_profiles()

    ## In case there are no instance profiles in the account ##
    if instance_profile_search['InstanceProfiles'] == []:
        print("No instance profiles found. Creating...")

    else:
        for i in range(0, len(instance_profile_search['InstanceProfiles'])):
            ## In case the instance profile already exists ##
            if instance_profile_search['InstanceProfiles'][i]['InstanceProfileName'] == 'instance_profile_for_ssm_tp3':
                print("Instance profile 'instance_profile_for_ssm_tp3' already exists.")
                return instance_profile_search['InstanceProfiles'][i]['Arn']
        print("There were other instance profiles, but not the one we need ('instance_profile_for_ssm_tp3'). Creating...")


    ## Creates the instance profile, below ##
    # Replace 'your_role_name' and 'your_policy_arn' with your actual values
    # POLICY_ARN SHOULD ALREADY EXIST!!
    role_name = 'iam_role_for_ssm_tp3'
    policy_arn = 'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'

    # Create an IAM role for SSM
    role_response = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument='{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
    )

    # Attach the SSM policy to the IAM role
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )

    # Create an IAM instance profile
    instance_profile_response = iam_client.create_instance_profile(
        InstanceProfileName='instance_profile_for_ssm_tp3',
    )

    # Associate the IAM role with the instance profile
    iam_client.add_role_to_instance_profile(
        InstanceProfileName=instance_profile_response['InstanceProfile']['InstanceProfileName'],
        RoleName=role_name
    )

    #print(instance_profile_response)

    #print(f"IAM Role Name: {role_name}")
    #print(f"IAM Role ARN: {role_response['Role']['Arn']}")
    #print(f"Instance Profile Name: {instance_profile_response['InstanceProfile']['InstanceProfileName']}")
    #print(f"Instance Profile ARN: {instance_profile_response['InstanceProfile']['Arn']}")

    return instance_profile_response['InstanceProfile']['Arn']

def create_instances(ec2, n, instance_type, image_id, security_group_id, user_data_script, key_pair_name, availability_zone, volume_size, instance_profile_arn):
    """
    Creates EC2 instances with the specified parameters.

    Args:
        ec2 (boto3.client): The EC2 client object.
        n (int): The number of instances to create.
        instance_type (str): The instance type to create.
        image_id (str): The ID of the AMI to use for the instances.
        security_group_id (str): The ID of the security group to assign to the instances.
        user_data_script (str): The user data script to run on the instances.
        key_pair_name (str): The name of the key pair to use for the instances.
        availability_zone (str): The availability zone in which to launch the instances.

    Returns:
        list: A list of the created EC2 instances.
    """

    instances = ec2.create_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'VolumeSize': volume_size,
                    'VolumeType': 'gp2'
                }
            },
        ],
        IamInstanceProfile={
            #'Name': 'string',
            'Arn': instance_profile_arn
        },
        MinCount=1,
        MaxCount=n,
        KeyName=key_pair_name,
        InstanceType=instance_type,
        ImageId=image_id,
        UserData=user_data_script,
        Placement={
            'AvailabilityZone': availability_zone
        },
        NetworkInterfaces=[
            {
                'DeviceIndex': 0,
                'Groups': [security_group_id],
                'AssociatePublicIpAddress': True
            }
        ],
        MetadataOptions={
            'HttpTokens': 'required' ## 'optional' or 'required'
        }
    )

    # register instances in target groups
    instance_ids = [instance.instance_id for instance in instances]
    print("Instance IDs:", instance_ids, " Availability zone:", availability_zone)

    for instance in instances:
        # Wait for each instance to be running
        instance.wait_until_running()

    return instances

def send_commands(ssm_client, instance_id, command): #### IDK IF THIS NEEDS SUDO OR NOT IN "COMMAND". PLS CHECK. SEEMS THAT's NOT NEEDED
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

    return 0

def create_files(ssm_client, instance_id, file_content, file_path):
    # Send the command to create the text file
    command = f'echo "{file_content}" > {file_path}'
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command]}
    )

    # Get the command ID
    command_id = response['Command']['CommandId']

    # Poll for the command completion status
    while True:
        command_status = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id
        ).get('Status')

        if command_status in ['Success', 'Failed', 'TimedOut', 'Canceled']:
            break

        time.sleep(5)  # Adjust the polling interval as needed

    print(f'Command Status: {command_status}')

    return 0

def append_files(ssm_client, instance_id, file_content, file_path):
    # Send the command to create the text file
    command = f'echo "{file_content}" >> {file_path}'
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command]}
    )

    # Get the command ID
    command_id = response['Command']['CommandId']
    print(command_id)

    # Poll for the command completion status
    waiter = ssm_client.get_waiter("command_executed")
    try:
        waiter.wait(
            CommandId=command_id,
            InstanceId=instance_id,
        )
    except WaiterError as ex:
        logging.error(ex)
        return

    return 0

def create_manager_file(ssm_client, instance_id, manager_private_ip_addresses, workers_private_ip_addresses):
    file_path = "/var/lib/mysql-cluster/config.ini"
    file_content = """[ndbd default]
# Options affecting ndbd processes on all data nodes:
NoOfReplicas=2	# Number of replicas

[ndb_mgmd]
# Management process options:
hostname=""" + manager_private_ip_addresses[0] + """
datadir=/var/lib/mysql-cluster 	# Directory for the log files

[ndbd]
hostname=""" + workers_private_ip_addresses[0] + """ # Hostname/IP of the first data node
NodeId=2			# Node ID for this data node
datadir=/usr/local/mysql/data	# Remote directory for the data files

[ndbd]
hostname=""" + workers_private_ip_addresses[1] + """ # Hostname/IP of the second data node
NodeId=3			# Node ID for this data node
datadir=/usr/local/mysql/data	# Remote directory for the data files

[mysqld]
# SQL node options:
hostname=""" + manager_private_ip_addresses[0] + """ # In our case the MySQL server/client is on the same Droplet as the cluster manager"""

    # Send the command to create the text file
    command = f'echo "{file_content}" > {file_path}'
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command]}
    )

    # Get the command ID
    command_id = response['Command']['CommandId']

    # Wait for the command to complete
    waiter = ssm_client.get_waiter('command_executed')
    waiter.wait(CommandId=command_id, InstanceId=instance_id)

    return 0

def create_worker_file(ssm_client, instance_id, manager_private_ip_addresses):
    file_path = "/etc/my.cnf"
    file_content = """[mysql_cluster]
# Options for NDB Cluster processes:
ndb-connectstring=""" + manager_private_ip_addresses[0] + """ # location of cluster manager"""

    # Send the command to create the text file
    command = f'echo "{file_content}" > {file_path}'
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': [command]}
    )

    # Get the command ID
    command_id = response['Command']['CommandId']

    # Wait for the command to complete
    waiter = ssm_client.get_waiter('command_executed')
    waiter.wait(CommandId=command_id, InstanceId=instance_id)

    return 0

def add_port_to_security_group():
    return 0

if __name__ == '__main__':
    pass
