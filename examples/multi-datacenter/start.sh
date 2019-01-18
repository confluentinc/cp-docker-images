#!/bin/bash

docker-compose up -d
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

./submit_replicator_dc1_to_dc2.sh
./submit_replicator_dc1_to_dc2_topic2.sh
./submit_replicator_dc2_to_dc1.sh
echo -e "\nsleeping 60s"
sleep 60

./read-topics.sh
