# Kafka in Docker With External Communication

This describes the configuration settings required to configure a Kafka Docker container to be compatible with consumers/producers from outside the Docker network, via host-mapped ports.

# Usage

Start the Docker containers:

```
docker-compose up -d
```

Note that Kafka is configured to listen on port `8000` with advertised host `localhost`.  This is the port that we will be using externally (from outside the docker network).

Start your `kafka-console-consumer`:

```
kafka-console-consumer --bootstrap-server localhost:8000 --topic test --from-beginning
```

Start your `kafka-console-producer`:

```
kafka-console-producer --broker-list localhost:8000 --topic test
```

Type text into the producer, see it appear in the consumer:

```
$ kafka-console-producer --broker-list localhost:8000 --topic test
>test
>test
>test01
>test02
>test03
```

and,

```
$ kafka-console-consumer --bootstrap-server localhost:8000 --topic test --from-beginning
[2018-07-10 21:57:59,282] WARN [Consumer clientId=consumer-1, groupId=console-consumer-62637] Error while fetching metadata with correlation id 2 : {test=LEADER_NOT_AVAILABLE} (org.apache.kafka.clients.NetworkClient)
[2018-07-10 21:57:59,443] WARN [Consumer clientId=consumer-1, groupId=console-consumer-62637] Error while fetching metadata with correlation id 4 : {test=LEADER_NOT_AVAILABLE} (org.apache.kafka.clients.NetworkClient)
test
test
test01
test02
test03
```
