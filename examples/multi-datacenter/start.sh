#!/bin/bash

docker-compose up -d
attempt=0
while [ $attempt -le 59 ]; do
    attempt=$(( $attempt + 1 ))
    result=$(docker-compose logs replicator-dc1-to-dc2)
    if grep -q 'Finished starting connectors and tasks' <<< $result ; then
      echo "Docker container replicator-dc1-to-dc2 is ready!"
      break
    fi
    echo "Waiting for Docker container replicator-dc1-to-dc2 to be ready"
    sleep 5
done
while [ $attempt -le 59 ]; do
    attempt=$(( $attempt + 1 ))
    result=$(docker-compose logs replicator-dc2-to-dc1)
    if grep -q 'Finished starting connectors and tasks' <<< $result ; then
      echo "Docker container replicator-dc2-to-dc1 is ready!"
      break
    fi
    sleep 5
    echo "Waiting for Docker container replicator-dc2-to-dc1 to be ready"
done

./submit_replicator_dc1_to_dc2.sh
./submit_replicator_dc2_to_dc1.sh
echo -e "\nsleeping 60s"
sleep 60

# The remainder of this script is purely to output some interesting data to help you understand the replication

echo -e "\n-----DC1-----"
echo -e "\nlist topics:"
docker-compose exec broker-dc1 kafka-topics --list --zookeeper zookeeper-dc1:2181
echo -e "\ntopic1:"
docker-compose exec schema-registry-dc1 kafka-avro-console-consumer --topic topic1 --bootstrap-server broker-dc1:9091 --property schema.registry.url=http://schema-registry-dc1:8081 --max-messages 10
echo -e "\n_schemas:"
docker-compose exec broker-dc1 kafka-console-consumer --topic _schemas --bootstrap-server broker-dc1:9091 --from-beginning --timeout-ms 5000
echo -e "\nprovenance info:"
docker-compose exec replicator-dc1-to-dc2 bash -c "export CLASSPATH=/usr/share/java/kafka-connect-replicator/kafka-connect-replicator-5.0.4-cp1.jar && kafka-console-consumer --topic topic1 --bootstrap-server broker-dc1:9091 --max-messages 10 --formatter=io.confluent.connect.replicator.tools.ProvenanceHeaderFormatter"
echo -e "\ncluster id:"
docker-compose exec zookeeper-dc1 zookeeper-shell localhost:2181 get /cluster/id | grep version | grep id | jq -r .id

echo -e "\n-----DC2-----"
echo -e "\nlist topics:"
docker-compose exec broker-dc2 kafka-topics --list --zookeeper zookeeper-dc2:2182
echo -e "\ntopic1:"
docker-compose exec schema-registry-dc1 kafka-avro-console-consumer --topic topic1 --bootstrap-server broker-dc2:9092 --property schema.registry.url=http://schema-registry-dc1:8081 --max-messages 10
echo -e "\n_schemas:"
docker-compose exec broker-dc1 kafka-console-consumer --topic _schemas --bootstrap-server broker-dc2:9092 --from-beginning --timeout-ms 5000
echo -e "\nprovenance info:"
docker-compose exec replicator-dc1-to-dc2 bash -c "export CLASSPATH=/usr/share/java/kafka-connect-replicator/kafka-connect-replicator-5.0.4-cp1.jar && kafka-console-consumer --topic topic1 --bootstrap-server broker-dc2:9092 --max-messages 10 --formatter=io.confluent.connect.replicator.tools.ProvenanceHeaderFormatter"
echo -e "\ncluster id:"
docker-compose exec zookeeper-dc2 zookeeper-shell localhost:2182 get /cluster/id | grep version | grep id | jq -r .id

