# Dockerfile for running Repeater Book data in container.

FROM python:3.9.10-slim-buster
WORKDIR /application
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python3", "getRepeaters.py"]
