""" 
    This is the main file for TP2, for the Advanced Cloud Computing course. 
"""

## Imports libraries publicly available. ##
import json
import sys
import time
import boto3

## Imports libraries created by us. ##
from creating_aws_objects import create_keypair, create_security_group, create_instances
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
    ## The 'client' variable creates a link to the EC2 service. ##
    client = boto3.client('ec2', region_name='us-east-1')

    ## EC2 client. ##
    ec2 = boto3.resource('ec2', region_name='us-east-1')

    response = client.get_console_output(
        InstanceId='i-0c1a336e1a8235088'
    )

    print(response)


##  Takes the program back to main(). ##
if __name__ == '__main__':
    main()