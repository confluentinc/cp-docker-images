import os
import unittest
import utils
import time
import string

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "zookeeper")
QUORUM_CHECK = "bash -c 'dub wait localhost {port} 30 && echo stat | nc localhost {port} | grep not && echo notready'"
MODE_COMMAND = "bash -c 'dub wait localhost {port} 30 && echo stat | nc localhost {port} | grep Mode'"


class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create directories with the correct permissions for test with userid and external volumes.
        utils.run_command_on_host(
            "mkdir -p /tmp/zk-config-kitchen-sink-test/data /tmp/zk-config-kitchen-sink-test/log")
        utils.run_command_on_host(
            "chown -R 12345 /tmp/zk-config-kitchen-sink-test/data /tmp/zk-config-kitchen-sink-test/log")

        cls.cluster = utils.TestCluster("config-test", FIXTURES_DIR, "standalone-config.yml")
        cls.cluster.start()

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()
        utils.run_command_on_host("rm -rf /tmp/zk-config-kitchen-sink-test")

    @classmethod
    def is_zk_healthy_for_service(cls, service, client_port):
        output = cls.cluster.run_command_on_service(service, MODE_COMMAND.format(port=client_port))
        assert "Mode: standalone\n" == output

    def test_required_config_failure(self):
        expected = "SERVER_ID is required."
        self.assertTrue(expected in self.cluster.service_logs("failing-config", stopped=True))

    def test_default_config(self):
        self.is_zk_healthy_for_service("default-config", 2181)
        import string
        zk_props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka/zookeeper.properties")
        expected = """tickTime=3000
            initLimit=10
            syncLimit=5

            dataDir=/opt/zookeeper/data
            dataLogDir=/opt/zookeeper/log

            clientPort=2181
            quorumListenOnAllIPs=true

            autopurge.purgeInterval=1
            autopurge.snapRetainCount=3
            """
        self.assertTrue(zk_props.translate(None, string.whitespace) == expected.translate(None, string.whitespace))

        zk_id = self.cluster.run_command_on_service("default-config", "cat /opt/zookeeper/data/myid")
        self.assertTrue(zk_id == "1")

    def test_full_config(self):
        self.is_zk_healthy_for_service("full-config", 22181)
        zk_props = self.cluster.run_command_on_service("full-config", "cat /etc/kafka/zookeeper.properties")
        expected = """tickTime=5555
                initLimit=25
                syncLimit=20

                dataDir=/opt/zookeeper/data
                dataLogDir=/opt/zookeeper/log

                clientPort=22181
                quorumListenOnAllIPs=false

                autopurge.purgeInterval=2
                autopurge.snapRetainCount=4
                """
        self.assertTrue(zk_props.translate(None, string.whitespace) == expected.translate(None, string.whitespace))

        zk_id = self.cluster.run_command_on_service("full-config", "cat /opt/zookeeper/data/myid")
        self.assertTrue(zk_id == "1")

    def test_volumes(self):
        self.is_zk_healthy_for_service("external-volumes", 2181)

    def test_random_user(self):
        self.is_zk_healthy_for_service("random-user", 2181)

    def test_kitchen_sink(self):
        self.is_zk_healthy_for_service("kitchen-sink", 22181)
        zk_props = self.cluster.run_command_on_service("kitchen-sink", "cat /etc/kafka/zookeeper.properties")
        expected = """tickTime=5555
                    initLimit=25
                    syncLimit=20

                    dataDir=/opt/zookeeper/data
                    dataLogDir=/opt/zookeeper/log

                    clientPort=22181
                    quorumListenOnAllIPs=false

                    autopurge.purgeInterval=2
                    autopurge.snapRetainCount=4
                    """
        self.assertTrue(zk_props.translate(None, string.whitespace) == expected.translate(None, string.whitespace))

        zk_id = self.cluster.run_command_on_service("full-config", "cat /opt/zookeeper/data/myid")
        self.assertTrue(zk_id == "1")


class StandaloneNetworkingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalone-network-test", FIXTURES_DIR, "standalone-network.yml")
        cls.cluster.start()

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_zk_healthy_for_service(cls, service, client_port):
        output = cls.cluster.run_command_on_service(service, MODE_COMMAND.format(port=client_port))
        assert "Mode: standalone\n" == output

    def test_bridge_network(self):
        # Test from within the container
        self.is_zk_healthy_for_service("bridge-network", 2181)
        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/zookeeper",
            command=MODE_COMMAND.format(port=22181),
            host_config={'NetworkMode': 'host'})
        self.assertEquals("Mode: standalone\n", logs)

    def test_host_network(self):
        # Test from within the container
        self.is_zk_healthy_for_service("host-network", 32181)
        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/zookeeper",
            command=MODE_COMMAND.format(port=32181),
            host_config={'NetworkMode': 'host'})
        self.assertEquals("Mode: standalone\n", logs)


class ClusterBridgeNetworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("cluster-test", FIXTURES_DIR, "cluster-bridged.yml")
        cls.cluster.start()

        # Wait for docker containers to bootup and zookeeper to finish leader election
        for _ in xrange(5):
            if cls.cluster.is_running():
                quorum_response = cls.cluster.run_command_on_all(QUORUM_CHECK.format(port=2181))
                print quorum_response
                if "notready" not in quorum_response:
                    break
            else:
                time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    def test_cluster_running(self):
        self.assertTrue(self.cluster.is_running())

    def test_zk_healthy(self):

        output = self.cluster.run_command_on_all(MODE_COMMAND.format(port=2181))
        print output
        expected = sorted(["Mode: follower\n", "Mode: follower\n", "Mode: leader\n"])

        self.assertEquals(sorted(output.values()), expected)

    def test_zk_serving_requests(self):
        client_ports = [22181, 32181, 42181]
        expected = sorted(["Mode: follower\n", "Mode: follower\n", "Mode: leader\n"])
        outputs = []

        for port in client_ports:
            output = utils.run_docker_command(
                image="confluentinc/zookeeper",
                command=MODE_COMMAND.format(port=port),
                host_config={'NetworkMode': 'host'})
            outputs.append(output)
        self.assertEquals(sorted(outputs), expected)


class ClusterHostNetworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("cluster-test", FIXTURES_DIR, "cluster-host.yml")
        cls.cluster.start()

        # Wait for docker containers to bootup and zookeeper to finish leader election
        for _ in xrange(5):
            if cls.cluster.is_running():
                quorum_response = cls.cluster.run_command_on_all(QUORUM_CHECK.format(port=2181))
                print quorum_response
                if "notready" not in quorum_response:
                    break
            else:
                time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    def test_cluster_running(self):
        self.assertTrue(self.cluster.is_running())

    def test_zk_serving_requests(self):
        client_ports = [22181, 32181, 42181]
        expected = sorted(["Mode: follower\n", "Mode: follower\n", "Mode: leader\n"])
        outputs = []

        for port in client_ports:
            output = utils.run_docker_command(
                image="confluentinc/zookeeper",
                command=MODE_COMMAND.format(port=port),
                host_config={'NetworkMode': 'host'})
            outputs.append(output)
        self.assertEquals(sorted(outputs), expected)
