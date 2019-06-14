#!/usr/bin/env bash

if [[ $(curl -s -o /dev/null -w %{http_code} http://$CONNECT_REST_ADVERTISED_HOST_NAME:$CONNECT_REST_PORT/) = 200 ]]; then
  echo "Woohoo! Kafka Connect is up!"
  exit 0
else 
  echo -e $(date) "\tKafka Connect HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://$CONNECT_REST_ADVERTISED_HOST_NAME:$CONNECT_REST_PORT/info) " (waiting for 200)"
  exit 1
fi
