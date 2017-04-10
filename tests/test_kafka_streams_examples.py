import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "kafka-streams-examples")
ZK_READY = "bash -c 'cub zk-ready {servers} 40 && echo PASS || echo FAIL'"
KAFKA_READY = "bash -c 'cub kafka-ready {num_brokers} 40 -z $KAFKA_ZOOKEEPER_CONNECT && echo PASS || echo FAIL'"
SR_READY = "bash -c 'cub sr-ready {host} {port} 20 && echo PASS || echo FAIL'"
KAFKA_MUSIC_APP_HEALTH_CHECK = "bash -c 'dub http-ready {url} 20 && echo PASS || echo FAIL'"

def props_to_list(props_str):
    return sorted([
        p.strip() for p in props_str.split("\n") if len(p.strip()) > 0
    ])

class ConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        machine_name = os.environ["DOCKER_MACHINE_NAME"]
        cls.machine = utils.TestMachine(machine_name)
        cls.cluster = utils.TestCluster("config-test", FIXTURES_DIR, "standalone-config.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper", ZK_READY.format(servers="localhost:2181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka", KAFKA_READY.format(num_brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("schema-registry", SR_READY.format(host="schema-registry", port=8081))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_kafka_music_app_healthy_for_service(cls, service):
        list_running_app_instances_url = "http://{host}:{port}/kafka-music/instances".format(host="localhost", port=7070)
        assert "PASS" in cls.cluster.run_command_on_service(service, KAFKA_MUSIC_APP_HEALTH_CHECK.format(url=list_running_app_instances_url))

    def test_required_config_failure(self):
        self.assertTrue("STREAMS_BOOTSTRAP_SERVERS is required." in self.cluster.service_logs("failing-config", stopped=True))

    def test_default_config(self):
        self.is_kafka_music_app_healthy_for_service("default-config")
        # The default config fixture does not contain any security-related settings.
        admin_props = props_to_list(self.cluster.run_command_on_service("default-config", "cat /etc/kafka-streams-examples/admin.properties"))
        expected_admin_props = []
        self.assertEquals(expected_admin_props, admin_props)
        # TODO: Once https://github.com/apache/kafka/pull/2815 is available for use,
        #       we should also validate some REST API responses (see `test_kafka_rest.py`)?

    def test_secure_config(self):
        output = self.cluster.run_command_on_service("secure-config", "bash -c 'while [ ! -f /tmp/config-is-done ]; do echo waiting && sleep 1; done; echo PASS'")
        assert "PASS" in output

        admin_props = props_to_list(self.cluster.run_command_on_service("secure-config", "cat /etc/kafka-streams-examples/admin.properties"))
        expected_admin_props = props_to_list("""
        producer.security.protocol=SSL
        producer.ssl.truststore.location=/path/to/producer-truststore
        producer.ssl.truststore.password=producer-password
        producer.ssl.keystore.location=/path/to/producer-keystore
        producer.ssl.keystore.password=producer-password
        producer.ssl.key.password=producer-password
        consumer.security.protocol=SSL
        consumer.ssl.truststore.location=/path/to/consumer-truststore
        consumer.ssl.truststore.password=consumer-password
        consumer.ssl.keystore.location=/path/to/consumer-keystore
        consumer.ssl.keystore.password=consumer-password
        consumer.ssl.key.password=consumer-password
        """)
        self.assertEquals(expected_admin_props, admin_props)


class StandaloneNetworkingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalone-network-test", FIXTURES_DIR, "standalone-network.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-bridge", ZK_READY.format(servers="localhost:12181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-bridge", KAFKA_READY.format(num_brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("schema-registry-bridge", SR_READY.format(host="schema-registry-bridge", port=18081))
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-host", ZK_READY.format(servers="localhost:32181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-host", KAFKA_READY.format(num_brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("schema-registry-host", SR_READY.format(host="localhost", port=38081))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_kafka_music_app_healthy_for_service(cls, service, port):
        list_running_app_instances_url = "http://{host}:{port}/kafka-music/instances".format(host="localhost", port=port)
        assert "PASS" in cls.cluster.run_command_on_service(service, KAFKA_MUSIC_APP_HEALTH_CHECK.format(url=list_running_app_instances_url))

    def test_bridged_network(self):
        # Verify access to the containerized application from inside its own container
        self.is_kafka_music_app_healthy_for_service("kafka-streams-examples-bridge", port=17070)

        # Verify outside access to the containerized application over the host network from a new container
        list_running_app_instances_url_host = "http://{host}:{port}/kafka-music/instances".format(host="localhost", port=27070)
        host_network_logs = utils.run_docker_command(
            image="confluentinc/cp-kafka-streams-examples",
            command=KAFKA_MUSIC_APP_HEALTH_CHECK.format(url=list_running_app_instances_url_host),
            host_config={'NetworkMode': 'host'})
        self.assertTrue("PASS" in host_network_logs)

        # Verify outside access to the containerized application over the bridge network from a new container
        list_running_app_instances_url_bridge = "http://{host}:{port}/kafka-music/instances".format(host="kafka-streams-examples-bridge", port=17070)
        bridge_network_logs = utils.run_docker_command(
            image="confluentinc/cp-kafka-streams-examples",
            command=KAFKA_MUSIC_APP_HEALTH_CHECK.format(url=list_running_app_instances_url_bridge),
            host_config={'NetworkMode': 'standalone-network-test_acme'})
        self.assertTrue("PASS" in bridge_network_logs)

    def test_host_network(self):
        # Verify access to the containerized application from inside its own container
        self.is_kafka_music_app_healthy_for_service("kafka-streams-examples-host", port=37070)

        # Verify outside access to the containerized application from a new container
        list_running_app_instances_url = "http://{host}:{port}/kafka-music/instances".format(host="localhost", port=37070)
        logs = utils.run_docker_command(
            image="confluentinc/cp-kafka-streams-examples",
            command=KAFKA_MUSIC_APP_HEALTH_CHECK.format(url=list_running_app_instances_url),
            host_config={'NetworkMode': 'host'})
        self.assertTrue("PASS" in logs)
