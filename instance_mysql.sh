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