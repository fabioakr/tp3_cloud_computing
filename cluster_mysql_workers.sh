#!/bin/bash

apt-get update
apt-get -y upgrade
apt-get -y install wget

cd ~
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.2/mysql-cluster-community-data-node_8.2.0-1ubuntu22.04_amd64.deb
apt-get -y install libclass-methodmaker-perl
dpkg -i mysql-cluster-community-data-node_8.2.0-1ubuntu22.04_amd64.deb

cd ~
cd /etc

echo "[mysql_cluster]
# Options for NDB Cluster processes:
ndb-connectstring=198.51.100.2  # location of cluster manager" | tee my.cnf

mkdir -p /usr/local/mysql/data

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