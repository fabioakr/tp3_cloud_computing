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

## Creates two different directories for each container. ##
mkdir composetest_one
mkdir composetest_two
cd composetest_one

## Creates files for first container and runs it. ##
echo "from flask import Flask, jsonify
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import random
import string

app = Flask(__name__)
# Load the pre-trained model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
def generate_random_text(length=50):
  letters = string.ascii_lowercase + ' '
  return ''.join(random.choice (letters) for i in range(length))


@app.route('/run_model', methods=['POST'])
def run_model():
  # Generate random input text
  input_text = generate_random_text()
  # Tokenize the input text and run it through the model
  inputs = tokenizer(input_text, return_tensors='pt', padding=True, truncation=True)
  outputs = model (**inputs)
  # The model returns logits, so let's turn that into probabilities
  probabilities = torch.softmax(outputs.logits, dim=-1)
  # Convert the tensor to a list and return
  probabilities_list = probabilities.tolist()[0]
  return jsonify({'input_text': input_text, 'probabilities': probabilities_list})


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)" | tee app.py

echo "flask" | tee requirements.txt

echo "# syntax=docker/dockerfile:1
FROM python:3.8
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install transformers
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu
EXPOSE 8000
COPY . .
CMD [\"flask\", \"run\"]" | tee Dockerfile


echo "services:
  web:
    build: .
    ports:
      - \"8000:8000\"" | tee compose.yaml

## Command that builds and runs the first container. ##
docker compose up -d

## Creates files for second container and runs it. ##
cd ..
cd composetest_two

echo "from flask import Flask, jsonify
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import random
import string

app = Flask(__name__)
# Load the pre-trained model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
def generate_random_text(length=50):
  letters = string.ascii_lowercase + ' '
  return ''.join(random.choice (letters) for i in range(length))


@app.route('/run_model', methods=['POST'])
def run_model():
  # Generate random input text
  input_text = generate_random_text()
  # Tokenize the input text and run it through the model
  inputs = tokenizer(input_text, return_tensors='pt', padding=True, truncation=True)
  outputs = model (**inputs)
  # The model returns logits, so let's turn that into probabilities
  probabilities = torch.softmax(outputs.logits, dim=-1)
  # Convert the tensor to a list and return
  probabilities_list = probabilities.tolist()[0]
  return jsonify({'input_text': input_text, 'probabilities': probabilities_list})


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8001)" | tee app.py

echo "flask" | tee requirements.txt

echo "# syntax=docker/dockerfile:1
FROM python:3.8
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8001
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install transformers
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu
EXPOSE 8001
COPY . .
CMD [\"flask\", \"run\"]" | tee Dockerfile


echo "services:
  web:
    build: .
    ports:
      - \"8001:8001\"" | tee compose.yaml

## Command that builds and runs the second container. ##
docker compose up -d