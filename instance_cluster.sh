#!/bin/bash

apt-get update
apt-get -y upgrade

## Steps for all instances ##
apt-get -y install wget
mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home
wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc
echo 'export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc' > /etc/profile.d/mysqlc.sh
echo 'export PATH=$MYSQLC_HOME/bin:$PATH' >> /etc/profile.d/mysqlc.sh
source /etc/profile.d/mysqlc.sh

## Steps for management node ##
mkdir -p /opt/mysqlcluster/deploy
cd /opt/mysqlcluster/deploy
mkdir conf
mkdir mysqld_data
mkdir ndb_data
cd conf

echo "[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306" | tee my.cnf

echo "[ndb_mgmd]
hostname=domU-12-31-39-04-D6-A3.compute-1.internal
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=2
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname=ip-10-72-50-247.ec2.internal
nodeid=3

[ndbd]
hostname=ip-10-194-139-246.ec2.internal
nodeid=4

[mysqld]
nodeid=50" | tee config.ini


