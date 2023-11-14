FROM python:3

RUN pip install boto3 requests

COPY tp2.py /

COPY creating_aws_objects.py /

COPY workloads.py /

COPY .env /

COPY instance_workers.sh /

COPY instance_orchestrator.sh /

COPY cleaning.py /

ENTRYPOINT ["python", "tp2.py"]
