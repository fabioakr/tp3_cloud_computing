""" 
    This module contains the most important functions made by us to create 
    AWS objects and allow for the necessary operations on TP2. 
"""

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
                    print(f"Inbound port '{port}' enabled in security group '{name}' .\n")
                else:
                    print(f"Inbound port '{port}' is already enabled in security group '{name}' .\n")
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
        print(f"Inbound port '{port}' enabled in security group '{name}' .\n")
    return security_group['GroupId']

def create_instances(ec2, n, instance_type, image_id, security_group_id, user_data_script, key_pair_name, availability_zone, volume_size):
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
        ]
    )

    # register instances in target groups
    instance_ids = [instance.instance_id for instance in instances]
    print("Instance IDs:", instance_ids, " Availability zone:", availability_zone)

    for instance in instances:
        # Wait for each instance to be running
        instance.wait_until_running()

    return instances

if __name__ == '__main__':
    pass
