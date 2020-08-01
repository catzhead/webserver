FROM debian:stable-slim

LABEL maintainer="catzhead@hotmail.com"
LABEL version="0.1"
LABEL description="uwsgi server for django applications"

# disable prompt during packages installation
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

RUN pip3 install uwsgi
