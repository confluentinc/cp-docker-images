import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "kafka-connect")
KAFKA_READY = "bash -c 'cub kafka-ready $KAFKA_ZOOKEEPER_CONNECT {brokers} 20 20 10 && echo PASS || echo FAIL'"
CONNECT_HEALTH_CHECK = "bash -c 'curl -X GET --fail --silent {host}:{port}/connectors && echo PASS || echo FAIL'"
ZK_READY = "bash -c 'cub zk-ready {servers} 10 10 2 && echo PASS || echo FAIL'"
SR_READY = "bash -c 'cub sr-ready {host} {port} 20 && echo PASS || echo FAIL'"
FILE_SOURCE_CONNECTOR_CREATE = """
    curl -X POST -H "Content-Type: application/json" \
    --data '{"name": "%s", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSourceConnector", "tasks.max":"1", "topic":"%s", "file": "%s"}}' \
    http://%s:%s/connectors
"""

FILE_SINK_CONNECTOR_CREATE = """
    curl -X POST -H "Content-Type: application/json" \
    --data '{"name": "%s", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector", "tasks.max":"1", "topics":"%s", "file": "%s"}}' \
    http://%s:%s/connectors
"""

CONNECTOR_STATUS = "curl -s -X GET http://{host}:{port}/connectors/{name}/status"


class ConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        machine_name = os.environ["DOCKER_MACHINE_NAME"]
        cls.machine = utils.TestMachine(machine_name)

        cls.cluster = utils.TestCluster("config-test", FIXTURES_DIR, "distributed-config.yml")
        cls.cluster.start()

        assert "PASS" in cls.cluster.run_command_on_service("zookeeper", ZK_READY.format(servers="localhost:2181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("schema-registry", SR_READY.format(host="schema-registry", port="8081"))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_connect_healthy_for_service(cls, service):
        output = cls.cluster.run_command_on_service(service, CONNECT_HEALTH_CHECK.format(host="localhost", port=8082))
        assert "PASS" in output

    def test_required_config_failure(self):
        self.assertTrue("CONNECT_BOOTSTRAP_SERVERS is required." in self.cluster.service_logs("failing-config", stopped=True))
        self.assertTrue("CONNECT_REST_PORT is required." in self.cluster.service_logs("failing-config-rest-port", stopped=True))
        self.assertTrue("CONNECT_CONFIG_STORAGE_TOPIC is required." in self.cluster.service_logs("failing-config-config-topic", stopped=True))
        self.assertTrue("CONNECT_OFFSET_STORAGE_TOPIC is required." in self.cluster.service_logs("failing-config-offset-topic", stopped=True))
        self.assertTrue("CONNECT_STATUS_STORAGE_TOPIC is required." in self.cluster.service_logs("failing-config-status-topic", stopped=True))
        self.assertTrue("CONNECT_KEY_CONVERTER is required." in self.cluster.service_logs("failing-config-key-converter", stopped=True))
        self.assertTrue("CONNECT_VALUE_CONVERTER is required." in self.cluster.service_logs("failing-config-value-converter", stopped=True))
        self.assertTrue("CONNECT_INTERNAL_KEY_CONVERTER is required." in self.cluster.service_logs("failing-config-internal-key-converter", stopped=True))
        self.assertTrue("CONNECT_INTERNAL_VALUE_CONVERTER is required." in self.cluster.service_logs("failing-config-internal-value-converter", stopped=True))
        self.assertTrue("CONNECT_ZOOKEEPER_CONNECT is required." in self.cluster.service_logs("failing-config-zookeeper-connect", stopped=True))

    def test_default_config(self):
        self.is_connect_healthy_for_service("default-config")
        props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka-connect/kafka-connect.properties")
        expected = """bootstrap.servers=kafka:9092
            rest.port=8082
            group.id=default
            config.storage.topic=default.config
            offset.storage.topic=default.offsets
            status.storage.topic=default.status
            key.converter=org.apache.kafka.connect.json.JsonConverter
            value.converter=org.apache.kafka.connect.json.JsonConverter
            internal.key.converter=org.apache.kafka.connect.json.JsonConverter
            internal.value.converter=org.apache.kafka.connect.json.JsonConverter
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_default_logging_config(self):
        self.is_connect_healthy_for_service("default-config")

        log4j_props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka-connect/log4j.properties")
        expected_log4j_props = """log4j.rootLogger=INFO, stdout

            log4j.appender.stdout=org.apache.log4j.ConsoleAppender
            log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
            log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n

            """
        self.assertEquals(log4j_props.translate(None, string.whitespace), expected_log4j_props.translate(None, string.whitespace))


class StandaloneNetworkingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("distributed-single-node", FIXTURES_DIR, "distributed-single-node.yml")
        cls.cluster.start()
        # assert "PASS" in cls.cluster.run_command_on_service("zookeeper-bridge", ZK_READY.format(servers="localhost:2181"))
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-host", ZK_READY.format(servers="localhost:32181"))
        # assert "PASS" in cls.cluster.run_command_on_service("kafka-bridge", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-host", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("schema-registry-host", SR_READY.format(host="localhost", port="8081"))

    # @classmethod
    # def tearDownClass(cls):
    #     cls.cluster.shutdown()

    @classmethod
    def is_connect_healthy_for_service(cls, service):
        output = cls.cluster.run_command_on_service(service, CONNECT_HEALTH_CHECK.format(host="localhost", port=28082))
        assert "PASS" in output

    def test_host_network(self):
        # Test from within the container
        self.is_connect_healthy_for_service("connect-host")

        # Create a file
        record_count = 10000

        # utils.run_docker_command(
        #     image="confluentinc/cp-kafka-connect",
        #     command="bash -c 'rm -rf /tmp/test/sink.test.txt && seq {count} > /tmp/test/source.test.txt'".format(count=record_count),
        #     host_config={'NetworkMode': 'host', 'Binds': ['/tmp/connect-file-test/:/tmp/test']})
        #
        # utils.run_docker_command(
        #     image="confluentinc/cp-kafka-connect",
        #     command=FILE_SOURCE_CONNECTOR_CREATE % ("one-node-source-test", "one-node-test", "/tmp/test/source.test.txt", "localhost", "28082"),
        #     host_config={'NetworkMode': 'host'})
        #
        # time.sleep(5)
        #
        # utils.run_docker_command(
        #     image="confluentinc/cp-kafka-connect",
        #     command=FILE_SINK_CONNECTOR_CREATE % ("one-node-sink-test", "one-node-test", "/tmp/test/sink.test.txt", "localhost", "28082"),
        #     host_config={'NetworkMode': 'host'})
        #
        # time.sleep(5)
        #
        # source_logs = utils.run_docker_command(
        #     image="confluentinc/cp-kafka-connect",
        #     command=CONNECTOR_STATUS.format(host="localhost", port="28082", name="one-node-source-test"),
        #     host_config={'NetworkMode': 'host'})
        #
        # source_connector = json.loads(source_logs)
        #
        # self.assertEquals(source_connector["connector"]["state"], "RUNNING")
        #
        # sink_logs = utils.run_docker_command(
        #     image="confluentinc/cp-kafka-connect",
        #     command=CONNECTOR_STATUS.format(host="localhost", port="28082", name="one-node-sink-test"),
        #     host_config={'NetworkMode': 'host'})
        #
        # sink_connector = json.loads(sink_logs)
        #
        # self.assertEquals(sink_connector["connector"]["state"], "RUNNING")
        #
        # logs = utils.run_docker_command(
        #     image="confluentinc/cp-kafka-connect",
        #     command="bash -c '[ -e /tmp/test/sink.test.txt ] && echo PASS || echo FAIL' ",
        #     host_config={'NetworkMode': 'host', 'Binds': ['/tmp/connect-file-test/:/tmp/test']})
        #
        # self.assertTrue("PASS" in logs)

        sink_record_count = utils.run_docker_command(
            image="confluentinc/cp-kafka-connect",
            command="bash -c 'wc -l /tmp/test/sink.test.txt | cut -d\" \" -f1'",
            host_config={'NetworkMode': 'host', 'Binds': ['/tmp/connect-file-test/:/tmp/test']})

        self.assertEquals(sink_record_count, record_count)
