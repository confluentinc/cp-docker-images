import os
import unittest
import utils
import docker

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "zookeeper")
MODE_COMMAND = "bash -c 'dub wait localhost {port} 20 && echo stat | nc localhost {port} | grep Mode'"

class ZookeeperFailingConfigTest(unittest.TestCase):

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


class ZookeeperClusterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalonetest", FIXTURES_DIR, "zookeeper-standalone-bridged.yml")
        cls.cluster.start()

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    def test_cluster_running(self):
        self.assertTrue(self.cluster.is_running())

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


class StandaloneZookeeperTestHostNetworking(unittest.TestCase):

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
