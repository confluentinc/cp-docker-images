import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "kafka-rest")
KAFKA_READY = "bash -c 'cub kafka-ready $ZOOKEEPER_CONNECT {brokers} 20 20 10 && echo PASS || echo FAIL'"
HEALTH_CHECK = "bash -c 'cub kr-ready {host} {port} 20 && echo PASS || echo FAIL'"
# POST_SCHEMA_CHECK = """curl -X POST -i -H "Content-Type: application/vnd.schemaregistry.v1+json" \
#     --data '{"schema": "{\\"type\\": \\"string\\"}"}' \
#     %s:%s/subjects/%s/versions"""
GET_TOPICS_CHECK = "bash -c 'curl -X GET -i {host}:{port}/topics'"
ZK_READY = "bash -c 'cub zk-ready {servers} 10 10 2 && echo PASS || echo FAIL'"
KAFKA_CHECK = "bash -c 'kafkacat -L -b {host}:{port} -J' "

class ConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        machine_name = os.environ["DOCKER_MACHINE_NAME"]
        cls.machine = utils.TestMachine(machine_name)

        cls.cluster = utils.TestCluster("config-test", FIXTURES_DIR, "standalone-config.yml")
        cls.cluster.start()

        assert "PASS" in cls.cluster.run_command_on_service("zookeeper", ZK_READY.format(servers="localhost:2181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka", KAFKA_READY.format(brokers=1))

    # @classmethod
    # def tearDownClass(cls):
    #     cls.cluster.shutdown()

    @classmethod
    def is_kafka_rest_healthy_for_service(cls, service):
        output = cls.cluster.run_command_on_service(service, HEALTH_CHECK.format(host="localhost",port=8082))
        assert "PASS" in output

    def test_required_config_failure(self):
        self.assertTrue("ZOOKEEPER_CONNECT is required." in self.cluster.service_logs("failing-config", stopped=True))

    def test_default_config(self):
        self.is_kafka_rest_healthy_for_service("default-config")
        props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka-rest/kafka-rest.properties")
        expected = """zookeeper.connect=zookeeper:2181/defaultconfig
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_default_logging_config(self):
        self.is_kafka_rest_healthy_for_service("default-config")

        log4j_props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka-rest/log4j.properties")
        expected_log4j_props = """log4j.rootLogger=INFO, stdout

            log4j.appender.stdout=org.apache.log4j.ConsoleAppender
            log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
            log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n

            """
        self.assertEquals(log4j_props.translate(None, string.whitespace), expected_log4j_props.translate(None, string.whitespace))

class StandaloneNetworkingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalone-network-test", FIXTURES_DIR, "standalone-network.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-bridge", ZK_READY.format(servers="localhost:2181"))
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-host", ZK_READY.format(servers="localhost:32181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-bridge", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-host", KAFKA_READY.format(brokers=1))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_kafka_rest_healthy_for_service(cls, service):
        output = cls.cluster.run_command_on_service(service, HEALTH_CHECK.format(host="localhost",port=8081))
        assert "PASS" in output

    def test_bridged_network(self):
        # Test from within the container
        self.is_kafka_rest_healthy_for_service("kafka-rest-bridge")
        # Test from outside the container on host network
        logs = utils.run_docker_command(
            image="confluentinc/kafka-rest",
            command=HEALTH_CHECK.format(host="localhost", port=18081),
            host_config={'NetworkMode': 'host'})

        self.assertTrue("PASS" in logs)

        # Test from outside the container on bridge network
        logs_2 = utils.run_docker_command(
            image="confluentinc/kafka-rest",
            command=HEALTH_CHECK.format(host="kafka-rest-bridge", port=8081),
            host_config={'NetworkMode': 'standalone-network-test_zk'})

        self.assertTrue("PASS" in logs_2)

    def test_host_network(self):
        # Test from within the container
        self.is_kafka_rest_healthy_for_service("kafka-rest-host")
        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/kafka-rest",
            command=HEALTH_CHECK.format(host="localhost", port=8081),
            host_config={'NetworkMode': 'host'})

        self.assertTrue("PASS" in logs)

