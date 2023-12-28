#!/bin/bash

apt-get update
apt-get -y upgrade
#apt-get -y install python3-pip
#apt-get -y install mysql-server
#service mysql start

apt-get -y install wget

## Installs tool that unzips stuff ##
## apt-get -y install unzip

#service mysqld stop
#yum remove mysql-server mysql mysql-devel

mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home

wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

echo ‘export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc’ > /etc/profile.d/mysqlc.sh
echo ‘export PATH=$MYSQLC_HOME/bin:$PATH’ >> /etc/profile.d/mysqlc.sh
source /etc/profile.d/mysqlc.sh




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