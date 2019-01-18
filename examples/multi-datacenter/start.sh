#!/bin/bash

docker-compose up -d

# Verify Kafka connect started
attempt=0
while [ $attempt -le 59 ]; do
    attempt=$(( $attempt + 1 ))
    result=$(docker-compose logs connect-dc2)
    if grep -q 'Finished starting connectors and tasks' <<< $result ; then
      echo "Docker container connect-dc2 is ready!"
      break
    fi
    echo "Waiting for Docker container connect-dc2 to be ready"
    sleep 5
done
while [ $attempt -le 59 ]; do
    attempt=$(( $attempt + 1 ))
    result=$(docker-compose logs connect-dc1)
    if grep -q 'Finished starting connectors and tasks' <<< $result ; then
      echo "Docker container connect-dc1 is ready!"
      break
    fi
    sleep 5
    echo "Waiting for Docker container connect-dc1 to be ready"
done

echo -e "\n\n./submit_replicator_dc1_to_dc2.sh"
./submit_replicator_dc1_to_dc2.sh
echo -e "\n\n./submit_replicator_dc1_to_dc2_topic.sh"
./submit_replicator_dc1_to_dc2_topic2.sh
echo -e "\n\n./submit_replicator_dc2_to_dc1.sh"
./submit_replicator_dc2_to_dc1.sh

echo -e "\nsleeping 60s"
sleep 60

# Verify Confluent Control Center has started within MAX_WAIT seconds
MAX_WAIT=300
CUR_WAIT=0
echo "Waiting up to $MAX_WAIT seconds for Confluent Control Center to start"
while [[ ! $(docker-compose logs control-center) =~ "Started NetworkTrafficServerConnector" ]]; do
  sleep 10
  CUR_WAIT=$(( CUR_WAIT+10 ))
  if [[ "$CUR_WAIT" -gt "$MAX_WAIT" ]]; then
    echo -e "\nERROR: The logs in control-center container do not show 'Started NetworkTrafficServerConnector' after $MAX_WAIT seconds. Please troubleshoot with 'docker-compose ps' and 'docker-compose logs'.\n"
    exit 1
  fi
done


./read-topics.sh
