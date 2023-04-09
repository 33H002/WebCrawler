FROM python:3.8

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    python3-dev  \
    default-libmysqlclient-dev \
    build-essential \
    libpcre3 libpcre3-dev

WORKDIR /usr/src/app

COPY . .
RUN pip install -r requirements.txt
