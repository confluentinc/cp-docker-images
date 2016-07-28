import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "control-center")
KAFKA_READY = "bash -c 'cub kafka-ready $KAFKA_ZOOKEEPER_CONNECT {brokers} 20 20 10 && echo PASS || echo FAIL'"
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

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_c3_healthy_for_service(cls, service):
        output = utils.run_docker_command(
            600,
            image="confluentinc/cp-control-center",
            command=C3_CHECK.format(host=service, port=9021),
            host_config={'NetworkMode': 'config-test_default'}
        )
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


class StandaloneNetworkingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalone-network-test", FIXTURES_DIR, "standalone-network.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-bridge", ZK_READY.format(servers="localhost:2181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-bridge", KAFKA_READY.format(brokers=1))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_c3_healthy_for_service(cls, service, network):
        output = utils.run_docker_command(
            600,
            image="confluentinc/cp-control-center",
            command=C3_CHECK.format(host=service, port=9021),
            host_config={'NetworkMode': network}
        )
        assert "PASS" in output

    def test_bridged_network(self):
        # Test from within the container
        self.is_c3_healthy_for_service("control-center-bridge", "standalone-network-test_zk")

        INTERCEPTOR_CLIENTS_CMD = """bash -xc '\
            export TOPIC="{topic}" \
            export MESSAGES="{messages}" \
            export CHECK_MESSAGES="{check_messages}"
            cub kafka-ready "$ZOOKEEPER_CONNECT" 1 20 20 10 \
            && control-center-run-class kafka.admin.TopicCommand --create --topic "$TOPIC" --partitions 1 --replication-factor 1 --if-not-exists --zookeeper "$ZOOKEEPER_CONNECT" \
            && echo "interceptor.classes=io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor" > /tmp/producer.config \
            && echo "acks=all" >> /tmp/producer.config \
            && seq "$MESSAGES" | control-center-run-class kafka.tools.ConsoleProducer --broker-list "$BOOTSTRAP_SERVERS" --topic "$TOPIC" \
            && echo PRODUCED "$MESSAGES" messages. \
            && echo "interceptor.classes=io.confluent.monitoring.clients.interceptor.MonitoringConsumerInterceptor" > /tmp/consumer.config \
            && control-center-run-class kafka.tools.ConsoleConsumer --bootstrap-server "$BOOTSTRAP_SERVERS" --topic "$TOPIC" --new-consumer --from-beginning --max-messages "$CHECK_MESSAGES" --consumer.config /tmp/consumer.config'
            """

        MESSAGES = 10000
        TOPIC = 'test-topic'
        # Run producer and consumer with interceptor to generate monitoring data
        out = utils.run_docker_command(
            image="confluentinc/cp-control-center",
            # TODO - check that all messages are read back when this bug is fixed - https://issues.apache.org/jira/browse/KAFKA-3993
            command=INTERCEPTOR_CLIENTS_CMD.format(topic=TOPIC, messages=MESSAGES, check_messages=MESSAGES // 2),
            host_config={'NetworkMode': 'standalone-network-test_zk'},
            environment={'ZOOKEEPER_CONNECT': 'zookeeper-bridge:2181', 'BOOTSTRAP_SERVERS': 'kafka-bridge:19092'}
        )
        self.assertTrue("PRODUCED %s messages" % MESSAGES in out)

        # Check that data was processed
        # Calculate last hour and next hour in case we cross the border
        now_unix = int(time.time())
        prev_hr_start_unix = now_unix - now_unix % 3600
        next_hr_start_unix = prev_hr_start_unix + 2 * 3600

        FETCH_MONITORING_DATA_CMD = """curl -s -H 'Content-Type: application/json' 'http://{host}:{port}/1.0/monitoring/consumer_groups?startTimeMs={start}&stopTimeMs={stop}&rollup=ONE_HOUR'"""
        cmd = FETCH_MONITORING_DATA_CMD.format(host="control-center-bridge", port=9021, start=prev_hr_start_unix * 1000, stop=next_hr_start_unix * 1000)

        fetch_cmd_args = {
            'image': "confluentinc/cp-control-center",
            'command': cmd,
            'host_config': {'NetworkMode': 'standalone-network-test_zk'},
        }

        attempts = 0
        while attempts <= 60:
            attempts += 1
            out = json.loads(utils.run_docker_command(**fetch_cmd_args))
            if 'error_code' in out and out['error_code'] == 404:
                time.sleep(5)
                continue
            else:
                self.assertTrue('sources' in out)
                self.assertEquals(1, len(out['sources']))
                self.assertEquals(TOPIC, out['sources'][0]['topic'])
                break
