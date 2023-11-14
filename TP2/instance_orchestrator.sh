#!/bin/bash

## Installs Docker in the instance. ##
apt-get -y install ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

## Creates a directory for the container. ##
mkdir orchestratorContainer
cd orchestratorContainer

## Creates files for orchestrator container and runs it. ##
echo "from flask import Flask, request, jsonify
import threading
import json
import time
import requests

app = Flask(__name__)
lock = threading.Lock()
response = None

def send_request_to_container(container_id, container_info):
        print(f'Sending request to {container_id}')
        url = 'http://' +  container_info['ip'] + ':' + container_info['port'] + '/run_model'
        request_response = requests.post(url, verify=False)
        global response
        response = {container_id : request_response.json()}
        print(request_response.json())
        
def update_container_status(container_id, status):
        with lock:
                with open('test.json', 'r') as f:
                        data = json.load(f)

                if container_id in data:
                        data[container_id]['status'] = status

                with open('test.json', 'w') as f:
                        json.dump(data, f)

def process_request():
        free_container = None
        while free_container == None:
                with lock:
                        with open('test.json', 'r') as f:
                                data = json.load(f)
                for container_id, container_info in data.items():
                        if container_info['status'] == 'free':
                                free_container = container_id
                                break

        update_container_status(free_container, 'busy')
        send_request_to_container(free_container, data[free_container])
        update_container_status(free_container, 'free')

@app.route('/orchestrator', methods=['POST'])
def myFlaskApp():
        request = threading.Thread(target=process_request)
        request.start()
        request.join()
        global response
        return response


if __name__ == \"__main__\":

       app.run(host='0.0.0.0', port=80) " | tee app.py

echo "flask" | tee requirements.txt

echo "#syntax=docker/dockerfile:1
FROM python:3.8
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install requests
EXPOSE 80
COPY . .
CMD [\"flask\", \"run\"]" | tee Dockerfile

echo "services:
  web:
    build: .
    ports:
      - \"80:80\"" | tee compose.yaml

## Command that builds and runs the orchestrator container. ##
docker compose up -d