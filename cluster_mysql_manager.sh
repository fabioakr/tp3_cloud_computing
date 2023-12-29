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

# Use this in case you're not able to set correct rules for enabling port 
#ufw disable 
# port 1186

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