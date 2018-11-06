docker-compose up -d
echo "sleeping 40s"
sleep 40

./submit_replicator_dc1_to_dc2.sh
./submit_replicator_dc2_to_dc1.sh
echo -e "\nsleeping 60s"
sleep 60

echo -e "\nDC1"
docker-compose exec broker-dc1 kafka-topics --list --zookeeper zookeeper-dc1:2181
docker-compose exec schema-registry-dc1 kafka-avro-console-consumer --topic topic1 --bootstrap-server broker-dc1:9091 --property schema.registry.url=http://schema-registry-dc1:8081 --max-messages 10
#docker-compose exec broker-dc1 kafka-run-class kafka.tools.DumpLogSegments --print-data-log --files /var/lib/kafka/data/topic1-0/00000000000000000000.log 
#docker-compose exec replicator-dc1-to-dc2 bash -c "export CLASSPATH=/usr/share/java/kafka-connect-replicator/kafka-connect-replicator-5.1.0-SNAPSHOT.jar && kafka-console-consumer --topic topic1 --bootstrap-server broker-dc1:9091 --max-messages 5 --formatter=io.confluent.connect.replicator.tools.ProvenanceHeaderFormatter"
docker-compose exec broker-dc1 kafka-console-consumer --topic _schemas --bootstrap-server broker-dc1:9091 --from-beginning --timeout-ms 5000

echo -e "\nDC2"
docker-compose exec broker-dc2 kafka-topics --list --zookeeper zookeeper-dc2:2182
docker-compose exec schema-registry-dc1 kafka-avro-console-consumer --topic topic1 --bootstrap-server broker-dc2:9092 --property schema.registry.url=http://schema-registry-dc1:8081 --max-messages 10
#docker-compose exec broker-dc2 kafka-run-class kafka.tools.DumpLogSegments --print-data-log --files /var/lib/kafka/data/topic1-0/00000000000000000000.log 
#docker-compose exec replicator-dc1-to-dc2 bash -c "export CLASSPATH=/usr/share/java/kafka-connect-replicator/kafka-connect-replicator-5.1.0-SNAPSHOT.jar && kafka-console-consumer --topic topic1 --bootstrap-server broker-dc2:9092 --max-messages 5 --formatter=io.confluent.connect.replicator.tools.ProvenanceHeaderFormatter"
docker-compose exec broker-dc1 kafka-console-consumer --topic _schemas --bootstrap-server broker-dc2:9092 --from-beginning --timeout-ms 5000
