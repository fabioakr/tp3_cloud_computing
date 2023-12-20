#!/bin/bash

apt-get update
apt-get -y upgrade
#apt-get -y install python3-pip
apt-get -y install mysql-server
service mysql start

## Installs tool that unzips stuff ##
apt-get -y install unzip

## Downloads and unzips the sakila database ##
apt-get -y install curl
curl -sS https://downloads.mysql.com/docs/sakila-db.zip > sakila-db.zip
unzip sakila-db.zip
cd sakila-db

## Installs the sakila database ##
#mysql -u root
#mysql
mysql -e "SOURCE sakila-schema.sql;"
mysql -e "SOURCE sakila-data.sql;"

## Installs sysbench ##
apt-get -y install sysbench

## Creates a few lines for testing? 
sysbench oltp_read_write --table-size=1000000 --mysql-db=sakila --mysql-user=root prepare
sysbench oltp_read_write --table-size=1000000 --threads=6 --time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root run > /var/log/bench_results.txt

## THIS CODE IS NOT WORKING. SUPPOSED FIRST TO BE COPYING THE FILE TO THE TERMINAL FOR US... ##
## CHECK FOR CHATGPT WHAT I ASKED. MAYBE THAT'S GONNA WORK AND CEST FINI ##
#cd /
#cd /var/log
#cat cloud-init-output.log

## To see if the sakila database was installed ##
## USE sakila;
## SHOW FULL TABLES;
## SELECT COUNT(*) FROM film;
## SELECT COUNT(*) FROM film_text;

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