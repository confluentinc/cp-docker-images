import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "kafka")
HEALTH_CHECK = "bash -c 'cub kafka-ready $ZOOKEEPER_CONNECT {brokers} 10 20 10 && echo PASS || echo FAIL'"
ZK_READY = "bash -c 'cub zk-ready {servers} 10 10 2 && echo PASS || echo FAIL'"
KAFKA_CHECK = "bash -c 'kafkacat -L -b {host}:{port} -J' "


class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create directories with the correct permissions for test with userid and external volumes.
        utils.run_command_on_host("mkdir -p /tmp/kafka-config-kitchen-sink-test/data")
        utils.run_command_on_host("chown -R 12345 /tmp/kafka-config-kitchen-sink-test/data")
        cls.cluster = utils.TestCluster("config-test", FIXTURES_DIR, "standalone-config.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper", ZK_READY.format(servers="localhost:2181"))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()
        utils.run_command_on_host("rm -rf /tmp/kafka-config-kitchen-sink-test")

    @classmethod
    def is_kafka_healthy_for_service(cls, service, num_brokers):
        output = cls.cluster.run_command_on_service(service, HEALTH_CHECK.format(brokers=num_brokers))
        assert "PASS" in output

    def test_required_config_failure(self):
        self.assertTrue("BROKER_ID is required." in self.cluster.service_logs("failing-config", stopped=True))
        self.assertTrue("ZOOKEEPER_CONNECT is required." in self.cluster.service_logs("failing-config-zk-connect", stopped=True))
        self.assertTrue("ADVERTISED_HOST_NAME is required." in self.cluster.service_logs("failing-config-adv-hostname", stopped=True))
        self.assertTrue("ADVERTISED_PORT is required." in self.cluster.service_logs("failing-config-adv-port", stopped=True))

    def test_default_config(self):
        self.is_kafka_healthy_for_service("default-config", 1)
        props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka/server.properties")
        expected = """broker.id=1
            advertised.host.name=default-config
            port=9092
            advertised.port=9092
            log.dirs=/opt/kafka/data
            zookeeper.connect=zookeeper:2181/defaultconfig
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_default_logging_config(self):
        self.is_kafka_healthy_for_service("default-config", 1)

        log4j_props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka/log4j.properties")
        expected_log4j_props = """log4j.rootLogger=INFO, stdout

            log4j.appender.stdout=org.apache.log4j.ConsoleAppender
            log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
            log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n


            log4j.logger.kafka.authorizer.logger=WARN, stdout
            log4j.logger.kafka.log.LogCleaner=INFO, stdout
            log4j.logger.kafka.producer.async.DefaultEventHandler=DEBUG, stdout
            log4j.logger.kafka.controller=TRACE, stdout
            log4j.logger.kafka.network.RequestChannel$=WARN, stdout
            log4j.logger.kafka.request.logger=WARN, stdout
            log4j.logger.state.change.logger=TRACE, stdout
            log4j.logger.kafka=INFO, stdout
            """
        self.assertEquals(log4j_props.translate(None, string.whitespace), expected_log4j_props.translate(None, string.whitespace))

        tools_log4j_props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka/tools-log4j.properties")
        expected_tools_log4j_props = """log4j.rootLogger=WARN, stderr

            log4j.appender.stderr=org.apache.log4j.ConsoleAppender
            log4j.appender.stderr.layout=org.apache.log4j.PatternLayout
            log4j.appender.stderr.layout.ConversionPattern=[%d] %p %m (%c)%n
            log4j.appender.stderr.Target=System.err
            """
        self.assertEquals(tools_log4j_props.translate(None, string.whitespace), expected_tools_log4j_props.translate(None, string.whitespace))

    def test_full_config(self):
        self.is_kafka_healthy_for_service("full-config", 1)
        props = self.cluster.run_command_on_service("full-config", "cat /etc/kafka/server.properties")
        expected = """broker.id=1
                advertised.host.name=full-config
                port=9092
                advertised.port=9092
                log.dirs=/opt/kafka/data
                zookeeper.connect=zookeeper:2181/fullconfig
                """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_full_logging_config(self):
        self.is_kafka_healthy_for_service("full-config", 1)

        log4j_props = self.cluster.run_command_on_service("full-config", "cat /etc/kafka/log4j.properties")
        expected_log4j_props = """log4j.rootLogger=WARN, stdout

            log4j.appender.stdout=org.apache.log4j.ConsoleAppender
            log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
            log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n


            log4j.logger.kafka.authorizer.logger=WARN, stdout
            log4j.logger.kafka.log.LogCleaner=INFO, stdout
            log4j.logger.kafka.producer.async.DefaultEventHandler=DEBUG, stdout
            log4j.logger.kafka.controller=WARN, stdout
            log4j.logger.kafka.network.RequestChannel$=WARN, stdout
            log4j.logger.kafka.request.logger=WARN, stdout
            log4j.logger.state.change.logger=TRACE, stdout
            log4j.logger.kafka.foo.bar=DEBUG, stdout
            log4j.logger.kafka=INFO, stdout
            """
        self.assertEquals(log4j_props.translate(None, string.whitespace), expected_log4j_props.translate(None, string.whitespace))

        tools_log4j_props = self.cluster.run_command_on_service("full-config", "cat /etc/kafka/tools-log4j.properties")
        expected_tools_log4j_props = """log4j.rootLogger=ERROR, stderr

            log4j.appender.stderr=org.apache.log4j.ConsoleAppender
            log4j.appender.stderr.layout=org.apache.log4j.PatternLayout
            log4j.appender.stderr.layout.ConversionPattern=[%d] %p %m (%c)%n
            log4j.appender.stderr.Target=System.err
            """
        self.assertEquals(tools_log4j_props.translate(None, string.whitespace), expected_tools_log4j_props.translate(None, string.whitespace))

    def test_volumes(self):
        self.is_kafka_healthy_for_service("external-volumes", 1)

    def test_random_user(self):
        self.is_kafka_healthy_for_service("random-user", 1)

    def test_kitchen_sink(self):
        self.is_kafka_healthy_for_service("kitchen-sink", 1)
        zk_props = self.cluster.run_command_on_service("kitchen-sink", "cat /etc/kafka/server.properties")
        expected = """broker.id=1
                advertised.host.name=kitchen-sink
                port=9092
                advertised.port=9092
                log.dirs=/opt/kafka/data
                zookeeper.connect=zookeeper:2181/kitchensink
                """
        self.assertTrue(zk_props.translate(None, string.whitespace) == expected.translate(None, string.whitespace))


class StandaloneNetworkingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalone-network-test", FIXTURES_DIR, "standalone-network.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper", ZK_READY.format(servers="localhost:2181"))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_kafka_healthy_for_service(cls, service, num_brokers):
        output = cls.cluster.run_command_on_service(service, HEALTH_CHECK.format(brokers=num_brokers))
        assert "PASS" in output

    def test_bridge_network(self):
        # Test from within the container
        self.is_kafka_healthy_for_service("kafka-bridge", 1)
        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/kafkacat",
            command=KAFKA_CHECK.format(host="localhost", port=19092),
            host_config={'NetworkMode': 'host'})

        parsed_logs = json.loads(logs)
        self.assertEquals(1, len(parsed_logs["brokers"]))
        self.assertEquals(1, parsed_logs["brokers"][0]["id"])
        self.assertEquals("localhost:19092", parsed_logs["brokers"][0]["name"])

    def test_host_network(self):
        # Test from within the container
        self.is_kafka_healthy_for_service("kafka-bridge", 1)
        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/kafkacat",
            command=KAFKA_CHECK.format(host="localhost", port=29092),
            host_config={'NetworkMode': 'host'})

        parsed_logs = json.loads(logs)
        self.assertEquals(1, len(parsed_logs["brokers"]))
        self.assertEquals(1, parsed_logs["brokers"][0]["id"])
        self.assertEquals("localhost:29092", parsed_logs["brokers"][0]["name"])


class ClusterBridgeNetworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("cluster-test", FIXTURES_DIR, "cluster-bridged.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-1", ZK_READY.format(servers="zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181"))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    def test_cluster_running(self):
        self.assertTrue(self.cluster.is_running())

    @classmethod
    def is_kafka_healthy_for_service(cls, service, num_brokers):
        output = cls.cluster.run_command_on_service(service, HEALTH_CHECK.format(brokers=num_brokers))
        assert "PASS" in output

    def test_bridge_network(self):
        # Test from within the container
        self.is_kafka_healthy_for_service("kafka-1", 3)
        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/kafkacat",
            command=KAFKA_CHECK.format(host="kafka-1", port=9092),
            host_config={'NetworkMode': 'cluster-test_zk'})

        parsed_logs = json.loads(logs)
        self.assertEquals(3, len(parsed_logs["brokers"]))
        expected_brokers = [{"id":1,"name":"kafka-1:9092"}, {"id":2,"name":"kafka-2:9092"}, {"id":3,"name":"kafka-3:9092"}]
        self.assertEquals(sorted(expected_brokers), sorted(parsed_logs["brokers"]))


class ClusterHostNetworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("cluster-test", FIXTURES_DIR, "cluster-host.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-1", ZK_READY.format(servers="localhost:22181,localhost:32181,localhost:42181"))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()
        pass

    def test_cluster_running(self):
        self.assertTrue(self.cluster.is_running())

    @classmethod
    def is_kafka_healthy_for_service(cls, service, num_brokers):
        output = cls.cluster.run_command_on_service(service, HEALTH_CHECK.format(brokers=num_brokers))
        assert "PASS" in output

    def test_bridge_network(self):
        # Test from within the container
        self.is_kafka_healthy_for_service("kafka-1", 3)
        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/kafkacat",
            command=KAFKA_CHECK.format(host="localhost", port=19092),
            host_config={'NetworkMode': 'host'})

        parsed_logs = json.loads(logs)
        self.assertEquals(3, len(parsed_logs["brokers"]))
        expected_brokers = [{"id":1,"name":"localhost:19092"}, {"id":2,"name":"localhost:29092"}, {"id":3,"name":"localhost:39092"}]
        self.assertEquals(sorted(expected_brokers), sorted(parsed_logs["brokers"]))
