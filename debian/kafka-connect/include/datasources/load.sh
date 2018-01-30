#!/bin/bash
#
BASEPATH="/datasources"
for FILE in $(ls $BASEPATH/*.json); do
  echo "$(date) => Scanning directory $BASEPATH"
  echo "$(date) => Found file $(basename $FILE)"
  payload=$(eval "echo "$(cat $FILE)"")
  curl -X POST -H "Content-Type: application/json" --data "$(echo $payload)" http://kafka-connect:8083/connectors
done
