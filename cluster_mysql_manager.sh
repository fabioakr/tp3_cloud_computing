#!/bin/bash

apt-get update
apt-get -y upgrade
#apt-get -y install python3-pip
#apt-get -y install mysql-server
#service mysql start

apt-get -y install wget

cd ~
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.2/mysql-cluster-community-management-server_8.2.0-1ubuntu22.04_amd64.deb
dpkg -i mysql-cluster-community-management-server_8.2.0-1ubuntu22.04_amd64.deb

mkdir /var/lib/mysql-cluster
cd ~
cd /var/lib/mysql-cluster/

echo "[ndbd default]
# Options affecting ndbd processes on all data nodes:
NoOfReplicas=3	# Number of replicas

[ndb_mgmd]
# Management process options:
hostname=198.51.100.2 # Hostname of the manager
datadir=/var/lib/mysql-cluster 	# Directory for the log files

[ndbd]
hostname=198.51.100.0 # Hostname/IP of the first data node
NodeId=2			# Node ID for this data node
datadir=/usr/local/mysql/data	# Remote directory for the data files

[ndbd]
hostname=198.51.100.1 # Hostname/IP of the second data node
NodeId=3			# Node ID for this data node
datadir=/usr/local/mysql/data	# Remote directory for the data files

[ndbd]
hostname=198.51.100.2 # Hostname/IP of the second data node
NodeId=4			# Node ID for this data node
datadir=/usr/local/mysql/data	# Remote directory for the data files

[mysqld]
# SQL node options:
hostname=198.51.100.2 # In our case the MySQL server/client is on the same Droplet as the cluster manager" | tee config.ini


## Installs tool that unzips stuff ##
## apt-get -y install unzip

#service mysqld stop
#yum remove mysql-server mysql mysql-devel


## How to run Ubuntu on Docker
## docker pull ubuntu
## docker run -i -t ubuntu /bin/bash
## https://dev.to/netk/getting-started-with-docker-running-an-ubuntu-image-4lk9
## https://electrictoolbox.com/run-single-mysql-query-command-line/
## https://dev.mysql.com/doc/sakila/en/sakila-installation.html
## https://www.datacamp.com/tutorial/my-sql-tutorial
## https://www.devart.com/dbforge/mysql/studio/how-to-show-all-database-list-in-mysql.html
## https://electrictoolbox.com/run-single-mysql-query-command-line/

## Instal nano for debug purposes 
## sudo apt install nano

## How to change .pem file permissions
## First access the path to the .pem file. Then run the following command:
## chmod 400 [name of file].pem