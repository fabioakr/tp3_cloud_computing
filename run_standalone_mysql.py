""" 
    This is the main file for TP2, for the Advanced Cloud Computing course. 
"""

## Imports libraries publicly available. ##
import json
import sys
import time
import boto3

## Imports libraries created by us. ##
from creating_aws_objects import create_keypair, create_security_group, create_instances, create_instance_profiles
from cleaning import main as cleaning_after_tests
from workloads import run_workloads


def create_workers_file(client, workers):
    ## uses a wait function on each instance to wait until instance starts running
    workers_ip_addresses = []
    for instance in workers:
        instance.wait_until_running()
        private_ip = instance.private_ip_address 
        
        # instance.reload() has to be done. If not, the public ip will be None
        # https://stackoverflow.com/questions/64664813/get-the-public-ipv4-address-of-a-newly-created-amazon-ec2-instance-with-boto3
        instance.reload()  

        public_ip = instance.public_ip_address
        workers_ip_addresses.append(public_ip)

    containers_json = {}

    ## Creating the notion of two containers located at diffenrent ports
    ## in each worker and keeping information about them in containers_json
    for idx, container in enumerate(workers_ip_addresses):
        containers_json[f'container{idx * 2 + 1}'] = {
            "ip": container,
            "port": "8000",
            "status": "free"
        }
        containers_json[f'container{idx * 2 + 2}'] = {
            "ip": container,
            "port": "8001",
            "status": "free"
        }
    ## Keeping this information in workers.json file
    with open("workers.json", "w") as f:
        f.write(json.dumps(containers_json))

    # insert the file in the instance
    with open("instance_orchestrator.sh", "r") as f:
        lines = f.readlines()

    ## Adds the string created in second argument to the array 
    ## lines as the one before last element
    lines.insert(-1, "echo '" + json.dumps(containers_json) + "'| tee test.json\n")

    ## Rewriting the instance_orchestrator.sh
    with open("instance_orchestrator.sh", "w") as f:
        f.writelines(lines)


def obtain_orchestrator_ip(orchestrator):
    orchestrator.wait_until_running()
    private_ip = orchestrator.private_ip_address

    ## Once more, orchestrator.reload() is necesarry otherwise the public IP will be None
    ## https://stackoverflow.com/questions/64664813/get-the-public-ipv4-address-of-a-newly-created-amazon-ec2-instance-with-boto3
    orchestrator.reload()

    public_ip = orchestrator.public_ip_address
    return public_ip


def main():
    ## Assign the number of threads and requests used
    n_threads = 12
    n_requests = 10

    ## Assigns region name to be used.
    region_name = 'us-east-1'

    ## Assigns key pair name to be used.
    key_pair_name = 'key_pair_tp3'

    ## If we put in three arguments they are used to specify the number of threads
    ## and requests. Otherwise we use default values
    if len(sys.argv) == 3:
        n_threads = int(sys.argv[1])
        n_requests = int(sys.argv[2])

    ## The 'client' variable creates a link to the EC2 service. ##
    client = boto3.client('ec2', region_name)

    ## EC2 client. ##
    ec2 = boto3.resource('ec2', region_name)

    ## IAM client. ##
    iam_client = boto3.client('iam')

    ## SSM client. ##
    ssm_client = boto3.client('ssm', region_name=region_name)

    ## Create keypair if it doesn't exist yet. ##
    key_pair = create_keypair(client, key_pair_name)

    ## Create security group if it doesn't exist yet. ##
    security_id_workers = create_security_group(client, 'security_group_workers', [22, 8000, 8001])

    ## Create instance profile if it doesn't exist yet. ##
    instance_profile_arn = create_instance_profiles(iam_client)

    ## Create instances. ##
    workers = create_instances(ec2,
                                1,
                                't2.micro',
                                'ami-053b0d53c279acc90',
                                security_id_workers,
                                open('instance_standalone_mysql.sh', 'r').read(),
                                key_pair,
                                'us-east-1a',
                                8,
                                instance_profile_arn)
    
    ## Collects instance ids. Needed for sending the command  ##
    ## to read the log file containing the benchmark results. ##
    instance_ids = [instance.instance_id for instance in workers]
    print(instance_ids[0])

    instance_id = instance_ids[0]

    ## Tells system to wait this time, so benchmark is there for sure. ##
    time.sleep(10)

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


'''
    # create workers.json file
    create_workers_file(ec2, workers)

    orchestrator_ip = obtain_orchestrator_ip(orchestrator[0])

    # Workloads
    run_workloads(orchestrator_ip, n_threads, n_requests)
'''
    ## Terminates all instances and load balancers to save up AWS credits. ##
    #time.sleep(5)
    #print("All images have been created. Now terminating all instances...")
    #cleaning_after_tests(client)


##  Takes the program back to main(). ##
if __name__ == '__main__':
    main()
