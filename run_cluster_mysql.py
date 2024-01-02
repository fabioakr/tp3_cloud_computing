""" 
    This is the main file for TP2, for the Advanced Cloud Computing course. 
"""

## Imports libraries publicly available. ##
import json
#import sys
import time
import boto3

## Imports libraries created by us. ##
from creating_aws_objects import create_keypair, create_security_group, create_instances
from creating_aws_objects import create_instance_profiles, send_commands, create_files
from creating_aws_objects import create_manager_file, create_worker_file, append_files
from creating_aws_objects import send_commands_without_waiter
from cleaning import main as cleaning_after_tests


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
    security_group_workers = create_security_group(client, 'security_group_workers', [22, 1186])
    print()
    security_group_manager = create_security_group(client, 'security_group_manager', [22, 1186])

    ## Create instance profile if it doesn't exist yet. ##
    print()
    instance_profile_arn = create_instance_profiles(iam_client)

    ## Creates worker instances ##
    print("\nCreating worker instances...")
    workers = create_instances(ec2,
                                3,
                                't2.micro',
                                'ami-053b0d53c279acc90',
                                security_group_workers,
                                open('cluster_mysql_workers.sh', 'r').read(),
                                key_pair,
                                'us-east-1a',
                                8,
                                instance_profile_arn)

    #print(workers[0].id)

    ## Gets public and private IP adress of each worker ##
    workers_private_ip_addresses = []
    workers_public_ip_addresses = []
    for instance in workers:
        instance.wait_until_running()
        instance.reload()
        # instance.reload() has to be done. If not, the public ip will be None
        # https://stackoverflow.com/questions/64664813/get-the-public-ipv4-address-of-a-newly-created-amazon-ec2-instance-with-boto3

        public_ip = instance.public_ip_address
        private_ip = instance.private_ip_address
        workers_private_ip_addresses.append(private_ip)
        workers_public_ip_addresses.append(public_ip)

    print("Private IPs:", workers_private_ip_addresses)
    print("Public IPs:", workers_public_ip_addresses)

    ## Creates manager instance ##
    print("\nCreating manager instance...")
    manager = create_instances(ec2,
                            1,
                            't2.micro',
                            'ami-053b0d53c279acc90',
                            security_group_manager,
                            open('cluster_mysql_manager.sh', 'r').read(),
                            key_pair,
                            'us-east-1a',
                            8,
                            instance_profile_arn)

    ## Gets public and private IP adress of the manager ##
    manager_private_ip_addresses = []
    manager_public_ip_addresses = []
    for instance in manager:
        instance.wait_until_running()
        instance.reload()
        # instance.reload() has to be done. If not, the public ip will be None
        # https://stackoverflow.com/questions/64664813/get-the-public-ipv4-address-of-a-newly-created-amazon-ec2-instance-with-boto3

        public_ip = instance.public_ip_address
        private_ip = instance.private_ip_address
        manager_private_ip_addresses.append(private_ip)
        manager_public_ip_addresses.append(public_ip)

    print("Private IPs:", manager_private_ip_addresses)
    print("Public IPs:", manager_public_ip_addresses)

    ## Waits for instances to run scripts completely ##
    print("\nWaiting for instances to run scripts completely... This will take a while!\n")
    time.sleep(200)

    ## Creates file in manager, containing all IPs of workers ##
    create_manager_file(ssm_client, manager[0].id, manager_private_ip_addresses, workers_private_ip_addresses)
    create_worker_file(ssm_client, workers[0].id, manager_private_ip_addresses)
    create_worker_file(ssm_client, workers[1].id, manager_private_ip_addresses)
    create_worker_file(ssm_client, workers[2].id, manager_private_ip_addresses)

    ## Enables manager node ##
    print("Enabling manager node...")
    send_commands(ssm_client, manager[0].instance_id, 'ndb_mgmd -f /var/lib/mysql-cluster/config.ini')

    ## Enables workers nodes ##
    for i in range(3):
        print(f"Enabling worker node {i}...")
        send_commands(ssm_client, workers[i].instance_id, 'ndbd')

    ## Enables MySQL server and client ##
    print("Enabling MySQL server and client on manager instance... This will take a while!")
    mysql_server_config = """cd ~
cd /var
mkdir installing
cd installing
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.2/mysql-cluster_8.2.0-1ubuntu22.04_amd64.deb-bundle.tar
mkdir install
tar -xvf mysql-cluster_8.2.0-1ubuntu22.04_amd64.deb-bundle.tar -C install/
cd install

apt-get update
apt-get -y install libaio1 libmecab2  ## IDK if here you need to reset your instance

dpkg -i mysql-common_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-client-plugins_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-client-core_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-client_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-client_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-server-core_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-server_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-server_8.2.0-1ubuntu22.04_amd64.deb
"""
    send_commands(ssm_client, manager[0].instance_id, mysql_server_config)

    ## Enables MySQL server and client ##
    print("Enabling MySQL server and client on worker instance... This will take a while!")
    file_path = '/etc/mysql/my.cnf'
    append_content = """
[mysqld]
# Options for mysqld process:
ndbcluster                      # run NDB storage engine

[mysql_cluster]
# Options for NDB Cluster processes:
ndb-connectstring=""" + manager_private_ip_addresses[0] + """   # location of management server"""
    append_files(ssm_client, manager[0].instance_id, append_content, file_path)

    mysql_restart = """systemctl restart mysql
sudo systemctl enable mysql"""
    #send_commands(ssm_client, manager[0].instance_id, mysql_restart)
    send_commands_without_waiter(ssm_client, manager[0].instance_id, mysql_restart)

    time.sleep(200)
    print("It's over!")

'''cd ~
cd /var
mkdir installing
cd installing
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.2/mysql-cluster_8.2.0-1ubuntu22.04_amd64.deb-bundle.tar
mkdir install
tar -xvf mysql-cluster_8.2.0-1ubuntu22.04_amd64.deb-bundle.tar -C install/
cd install

apt-get update
apt-get -y install libaio1 libmecab2  ## IDK if here you need to reset your instance

dpkg -i mysql-common_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-client-plugins_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-client-core_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-client_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-client_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-server-core_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-server_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-server_8.2.0-1ubuntu22.04_amd64.deb'''

##  Takes the program back to main(). ##
if __name__ == '__main__':
    main()
