# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

ENV EXCHANGE_EMAIL="user@email.com"
ENV EXCHANGE_PASS="password"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD python3 main.py -e $EXCHANGE_EMAIL -p $EXCHANGE_PASS
