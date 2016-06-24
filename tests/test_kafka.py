import os
import unittest
import utils
import time
import string

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "kafka")
HEALTH_CHECK = "bash -c 'cub kafka-ready $ZOOKEEPER_CONNECT {brokers} 10 10 10 && echo PASS || echo FAIL'"
ZK_READY = "bash -c 'cub zk-ready localhost:2181 10 10 2 && echo PASS || echo FAIL'"

class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create directories with the correct permissions for test with userid and external volumes.
        utils.run_command_on_host("mkdir -p /tmp/kafka-config-kitchen-sink-test/data")
        utils.run_command_on_host("chown -R 12345 /tmp/kafka-config-kitchen-sink-test/data")
        cls.cluster = utils.TestCluster("config-test", FIXTURES_DIR, "standalone-config.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper", ZK_READY)

    @classmethod
    def tearDownClass(cls):
        # cls.cluster.shutdown()
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

    def test_rdefault_config(self):
        self.is_kafka_healthy_for_service("default-config", 1)
        import string
        props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka/server.properties")
        expected = """broker.id=1
            advertised.host.name=default-config
            port=9092
            advertised.port=9092
            log.dirs=/opt/kafka/data
            zookeeper.connect=zookeeper:2181/defaultconfig
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

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


# class StandaloneNetworkingTest(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.cluster = utils.TestCluster("standalone-network-test", FIXTURES_DIR, "standalone-network.yml")
#         cls.cluster.start()
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.cluster.shutdown()
#
#     @classmethod
#     def is_zk_healthy_for_service(cls, service, client_port):
#         output = cls.cluster.run_command_on_service(service, MODE_COMMAND.format(port=client_port))
#         assert "Mode: standalone\n" == output
#
#     def test_bridge_network(self):
#         # Test from within the container
#         self.is_zk_healthy_for_service("bridge-network", 2181)
#         # Test from outside the container
#         logs = utils.run_docker_command(
#             image="confluentinc/zookeeper",
#             command=MODE_COMMAND.format(port=22181),
#             host_config={'NetworkMode': 'host'})
#         self.assertEquals("Mode: standalone\n", logs)
#
#     def test_host_network(self):
#         # Test from within the container
#         self.is_zk_healthy_for_service("host-network", 32181)
#         # Test from outside the container
#         logs = utils.run_docker_command(
#             image="confluentinc/zookeeper",
#             command=MODE_COMMAND.format(port=32181),
#             host_config={'NetworkMode': 'host'})
#         self.assertEquals("Mode: standalone\n", logs)
#
#
# class ClusterBridgeNetworkTest(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.cluster = utils.TestCluster("cluster-test", FIXTURES_DIR, "cluster-bridged.yml")
#         cls.cluster.start()
#
#         # Wait for docker containers to bootup and zookeeper to finish leader election
#         for _ in xrange(5):
#             if cls.cluster.is_running():
#                 quorum_response = cls.cluster.run_command_on_all(QUORUM_CHECK.format(port=2181))
#                 print quorum_response
#                 if "notready" not in quorum_response:
#                     break
#             else:
#                 time.sleep(1)
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.cluster.shutdown()
#
#     def test_cluster_running(self):
#         self.assertTrue(self.cluster.is_running())
#
#     def test_zk_healthy(self):
#
#         output = self.cluster.run_command_on_all(MODE_COMMAND.format(port=2181))
#         print output
#         expected = sorted(["Mode: follower\n", "Mode: follower\n", "Mode: leader\n"])
#
#         self.assertEquals(sorted(output.values()), expected)
#
#     def test_zk_serving_requests(self):
#         client_ports = [22181, 32181, 42181]
#         expected = sorted(["Mode: follower\n", "Mode: follower\n", "Mode: leader\n"])
#         outputs = []
#
#         for port in client_ports:
#             output = utils.run_docker_command(
#                 image="confluentinc/zookeeper",
#                 command=MODE_COMMAND.format(port=port),
#                 host_config={'NetworkMode': 'host'})
#             outputs.append(output)
#         self.assertEquals(sorted(outputs), expected)
#
#
# class ClusterHostNetworkTest(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.cluster = utils.TestCluster("cluster-test", FIXTURES_DIR, "cluster-bridged.yml")
#         cls.cluster.start()
#
#         # Wait for docker containers to bootup and zookeeper to finish leader election
#         for _ in xrange(5):
#             if cls.cluster.is_running():
#                 quorum_response = cls.cluster.run_command_on_all(QUORUM_CHECK.format(port=2181))
#                 print quorum_response
#                 if "notready" not in quorum_response:
#                     break
#             else:
#                 time.sleep(1)
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.cluster.shutdown()
#
#     def test_cluster_running(self):
#         self.assertTrue(self.cluster.is_running())
#
#     def test_zk_serving_requests(self):
#         client_ports = [22181, 32181, 42181]
#         expected = sorted(["Mode: follower\n", "Mode: follower\n", "Mode: leader\n"])
#         outputs = []
#
#         for port in client_ports:
#             output = utils.run_docker_command(
#                 image="confluentinc/zookeeper",
#                 command=MODE_COMMAND.format(port=port),
#                 host_config={'NetworkMode': 'host'})
#             outputs.append(output)
#         self.assertEquals(sorted(outputs), expected)
