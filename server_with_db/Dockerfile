# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /home/

COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 6000
CMD [ "python3", "./server.py" ]
