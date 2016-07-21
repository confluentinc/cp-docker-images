import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "control-center")
KAFKA_READY = "bash -c 'cub kafka-ready $ZOOKEEPER_CONNECT {brokers} 20 20 10 && echo PASS || echo FAIL'"
ZK_READY = "bash -c 'cub zk-ready {servers} 10 10 2 && echo PASS || echo FAIL'"
C3_CHECK = "bash -c 'dub wait {host} {port} 240 && curl -fs -X GET -i {host}:{port}/ && echo PASS || echo FAIL'"


class ConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ['DOCKER_CLIENT_TIMEOUT'] = "600"
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
    def is_c3_healthy_for_service(cls, service):
        output = utils.run_docker_command(
            600,
            image="confluentinc/control-center",
            command=C3_CHECK.format(host=service, port=9021),
            host_config={'NetworkMode': 'config-test_default'}
        )
        # output = cls.cluster.run_command_on_service(service, C3_CHECK.format(host="localhost", port=9021))
        assert "PASS" in output

    def test_required_config_failure(self):
        self.assertTrue("BOOTSTRAP_SERVERS is required." in self.cluster.service_logs("failing-config", stopped=True))
        self.assertTrue("ZOOKEEPER_CONNECT is required." in self.cluster.service_logs("failing-config-missing-zk-connect", stopped=True))
        self.assertTrue("CONTROL_CENTER_REPLICATION_FACTOR is required." in self.cluster.service_logs("failing-config-missing-rep-factor", stopped=True))

    def test_default_config(self):
        self.is_c3_healthy_for_service("default-config")
        props = self.cluster.run_command_on_service("default-config", "cat /etc/confluent-control-center/control-center.properties")
        expected = """
        bootstrap.servers=kafka:9092
        zookeeper.connect=zookeeper:2181/defaultconfig
        confluent.controlcenter.data.dir=/var/lib/confluent-control-center
        confluent.monitoring.interceptor.topic.replication=1
        confluent.controlcenter.internal.topics.replication=1
        """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    # def test_default_logging_config(self):
    #     self.is_schema_registry_healthy_for_service("default-config")
    #
    #     log4j_props = self.cluster.run_command_on_service("default-config", "cat /etc/schema-registry/log4j.properties")
    #     expected_log4j_props = """log4j.rootLogger=INFO, stdout
    #
    #         log4j.appender.stdout=org.apache.log4j.ConsoleAppender
    #         log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
    #         log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n
    #
    #         """
    #     self.assertEquals(log4j_props.translate(None, string.whitespace), expected_log4j_props.translate(None, string.whitespace))
