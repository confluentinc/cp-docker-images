import os
import unittest
import utils
import docker
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "zookeeper")
QUORUM_CHECK = "bash -c 'dub wait localhost {port} 30 && echo stat | nc localhost {port} | grep not && echo notready'"
MODE_COMMAND = "bash -c 'dub wait localhost {port} 30 && echo stat | nc localhost {port} | grep Mode'"


class FailingConfigTest(unittest.TestCase):

    def setUp(self):
        self.image = "confluentinc/zookeeper"
        client = docker.from_env(assert_hostname=False)
        self.container = utils.TestContainer.create(client, image=self.image)
        self.container.start()

    def tearDown(self):
        self.container.shutdown()

    def test_required_config_failure(self):
        expected = "SERVER_ID is required."
        self.container.wait()
        output = self.container.logs()
        print output
        self.assertTrue(expected in output)


class StandaloneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalonetest", FIXTURES_DIR, "zookeeper-standalone-bridged.yml")
        cls.cluster.start()

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    def test_cluster_running(self):
        self.assertTrue(self.cluster.is_running())

    def test_zk_healthy(self):
        output = self.cluster.run_command_on_service("zookeeper", MODE_COMMAND.format(port=2181))
        self.assertEquals("Mode: standalone\n", output)

    def test_config_correct(self):
        import string
        file_contents = self.cluster.run_command_on_service("zookeeper", "cat /etc/kafka/zookeeper.properties")
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
        self.assertTrue(file_contents.translate(None, string.whitespace) == expected.translate(None, string.whitespace))

    def test_zk_serving_requests(self):
        logs = utils.run_docker_command(
                                     image="confluentinc/zookeeper",
                                     command=MODE_COMMAND.format(port=22181),
                                     host_config={'NetworkMode': 'host'})
        self.assertEquals("Mode: standalone\n", logs)


class StandaloneWithHostNetworkingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalone-host-test", FIXTURES_DIR, "zookeeper-standalone-host.yml")
        cls.cluster.start()

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    def test_zk_healthy(self):
        output = self.cluster.run_command_on_service(
            "zookeeper",
            MODE_COMMAND.format(port=22181))
        self.assertEquals("Mode: standalone\n", output)

    def test_zk_serving_requests(self):
        logs = utils.run_docker_command(
            image="confluentinc/zookeeper",
            command=MODE_COMMAND.format(port=22181),
            host_config={'NetworkMode': 'host'})
        self.assertEquals("Mode: standalone\n", logs)


class ClusterWithBridgeNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("cluster-bridge-test", FIXTURES_DIR, "zookeeper-cluster-bridged.yml")
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
        self.assertEquals(outputs, expected)
