import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "enterprise-replicator")
KAFKA_READY = "bash -c 'cub kafka-ready {brokers} 40 -z $KAFKA_ZOOKEEPER_CONNECT && echo PASS || echo FAIL'"
CONNECT_HEALTH_CHECK = "bash -c 'dub wait {host} {port} 30 && curl -X GET --fail --silent {host}:{port}/connectors && echo PASS || echo FAIL'"
ZK_READY = "bash -c 'cub zk-ready {servers} 40 && echo PASS || echo FAIL'"
TOPIC_CREATE = "bash -c ' kafka-topics --create --topic {name} --partitions {partitions} --replication-factor {replicas} --if-not-exists --zookeeper $KAFKA_ZOOKEEPER_CONNECT && echo PASS || echo FAIL' "

REPLICATOR_CREATE = """
    curl -X POST -H "Content-Type: application/json" \
    --data '{"name": "%s",
            "config": {
            "connector.class":"io.confluent.connect.replicator.ReplicatorSourceConnector",
            "key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
            "value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
            "src.zookeeper.connect": "%s",
            "src.kafka.bootstrap.servers": "%s",
            "dest.zookeeper.connect": "%s",
            "topic.whitelist": "%s",
            "topic.rename.format": "${topic}.replica"}}' \
    http://%s:%s/connectors
"""

CONNECTOR_STATUS = "curl -s -X GET http://{host}:{port}/connectors/{name}/status"

PRODUCE_DATA = """bash -c "\
    seq {messages} | kafka-console-producer --broker-list {brokers} --topic {topic}  \
    && echo PASS || echo FAIL"
    """

CONSUME_DATA = """bash -c "\
        export KAFKA_TOOLS_LOG4J_LOGLEVEL=DEBUG \
        && dub template "/etc/confluent/docker/tools-log4j.properties.template" "/etc/kafka/tools-log4j.properties" \
        && kafka-console-consumer --bootstrap-server {brokers} --topic {topic} --from-beginning --max-messages {messages}"
        """


def create_connector(name, create_command, host, port):

    utils.run_docker_command(
        image="confluentinc/cp-kafka-connect",
        command=create_command,
        host_config={'NetworkMode': 'host'})

    status = None
    for i in xrange(25):
        source_logs = utils.run_docker_command(
            image="confluentinc/cp-kafka-connect",
            command=CONNECTOR_STATUS.format(host=host, port=port, name=name),
            host_config={'NetworkMode': 'host'})

        connector = json.loads(source_logs)
        # Retry if you see errors, connect might still be creating the connector.
        if "error_code" in connector:
            time.sleep(1)
        else:
            status = connector["connector"]["state"]
            if status == "FAILED":
                return status
            elif status == "RUNNING":
                return status
            elif status == "UNASSIGNED":
                time.sleep(1)

    return status


class ClusterHostNetworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        machine_name = os.environ["DOCKER_MACHINE_NAME"]
        cls.machine = utils.TestMachine(machine_name)

        # Copy SSL files.
        cls.base_dir = "/tmp/replicator-host-cluster-test"
        cls.cluster = utils.TestCluster("replicator-test", FIXTURES_DIR, "cluster-host-plain.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-src-a", ZK_READY.format(servers="localhost:22181"))
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-src-b", ZK_READY.format(servers="localhost:32181"))
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-dest", ZK_READY.format(servers="localhost:42181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-1-src-a", KAFKA_READY.format(brokers=2))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-1-src-a", KAFKA_READY.format(brokers=2))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-1-dest", KAFKA_READY.format(brokers=2))

    @classmethod
    def tearDownClass(cls):
        cls.machine.ssh("sudo rm -rf %s" % cls.base_dir)
        cls.cluster.shutdown()

    def create_topic(self, kafka_service, topic, partitions=1, replicas=1):
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=topic, partitions=partitions, replicas=replicas))

    def test_cluster_running(self):
        self.assertTrue(self.cluster.is_running())

    @classmethod
    def is_connect_healthy_for_service(cls, service, port):
        assert "PASS" in cls.cluster.run_command_on_service(service, CONNECT_HEALTH_CHECK.format(host="localhost", port=port))

    def test_replicator(self):

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topic("kafka-1-dest", "replicator.config")
        self.create_topic("kafka-1-dest", "replicator.offsets")
        self.create_topic("kafka-1-dest", "replicator.status")

        self.create_topic("kafka-1-src-a", "foo", 3, 2)
        self.create_topic("kafka-1-src-b", "bar", 3, 2)

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-1", 28082)
        self.is_connect_healthy_for_service("connect-host-2", 38082)

        assert "PASS" in self.cluster.run_command_on_service("kafka-1-src-a", PRODUCE_DATA.format(messages=1000, brokers="localhost:9092", topic="foo"))
        assert "PASS" in self.cluster.run_command_on_service("kafka-1-src-b", PRODUCE_DATA.format(messages=1000, brokers="localhost:9082", topic="bar"))

        src_a_replicator_cmd = REPLICATOR_CREATE % ("cluster-a", "localhost:22181", "localhost:9092", "localhost:42181", "foo", "localhost", "28082")
        src_a_replicator = create_connector("cluster-a", src_a_replicator_cmd, "localhost", "28082")
        self.assertEquals(src_a_replicator, "RUNNING")

        src_b_replicator_cmd = REPLICATOR_CREATE % ("cluster-b", "localhost:32181", "localhost:9082", "localhost:42181", "bar", "localhost", "28082")
        src_b_replicator = create_connector("cluster-b", src_b_replicator_cmd, "localhost", "28082")
        self.assertEquals(src_b_replicator, "RUNNING")

        foo_consumer_logs = self.cluster.run_command_on_service("kafka-1-src-a", CONSUME_DATA.format(messages=1000, brokers="localhost:9072", topic="foo.replica"))
        self.assertTrue("Processed a total of 1000 messages" in foo_consumer_logs)

        bar_consumer_logs = self.cluster.run_command_on_service("kafka-1-src-b", CONSUME_DATA.format(messages=1000, brokers="localhost:9072", topic="bar.replica"))
        self.assertTrue("Processed a total of 1000 messages" in bar_consumer_logs)
