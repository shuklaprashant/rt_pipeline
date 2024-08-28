FROM alpine:3.14.1

ARG PRODUCER_MAX_SLEEP_TIME_SECONDS=5
ARG TOTAL_EVENTS_TO_GENERATE=10000
WORKDIR /app

RUN apk add --update py-pip

COPY requirements.txt .
COPY src ./src

RUN pip install -r requirements.txt
