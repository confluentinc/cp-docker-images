import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "kafka-connect")
KAFKA_READY = "bash -c 'cub kafka-ready $KAFKA_ZOOKEEPER_CONNECT {brokers} 20 20 10 && echo PASS || echo FAIL'"
CONNECT_HEALTH_CHECK = "bash -c 'dub wait {host} {port} 30 && curl -X GET --fail --silent {host}:{port}/connectors && echo PASS || echo FAIL'"
ZK_READY = "bash -c 'cub zk-ready {servers} 10 10 2 && echo PASS || echo FAIL'"
SR_READY = "bash -c 'cub sr-ready {host} {port} 20 && echo PASS || echo FAIL'"

TOPIC_CREATE = "bash -c ' kafka-topics --create --topic {name} --partitions 1 --replication-factor 1 --if-not-exists --zookeeper $KAFKA_ZOOKEEPER_CONNECT && echo PASS || echo FAIL' "

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

JDBC_SOURCE_CONNECTOR_CREATE = """
    curl -X POST -H "Content-Type: application/json" --data '{ "name": "%s", "config": { "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector", "tasks.max": 1, "connection.url": "%s", "mode": "incrementing", "incrementing.column.name": "id", "timestamp.column.name": "modified", "topic.prefix": "%s", "poll.interval.ms": 1000 } }' \
    http://%s:%s/connectors
"""

CONNECTOR_STATUS = "curl -s -X GET http://{host}:{port}/connectors/{name}/status"


class ConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

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
        self.assertTrue("CONNECT_REST_ADVERTISED_HOST_NAME is required." in self.cluster.service_logs("failing-config-rest-adv-host-name", stopped=True))
        self.assertTrue("CONNECT_ZOOKEEPER_CONNECT is required." in self.cluster.service_logs("failing-config-zookeeper-connect", stopped=True))

    def test_default_config(self):
        self.is_connect_healthy_for_service("default-config")
        props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka-connect/kafka-connect.properties")
        expected = """bootstrap.servers=kafka:9092
            rest.port=8082
            rest.advertised.host.name=default-config
            group.id=default
            config.storage.topic=default.config
            offset.storage.topic=default.offsets
            status.storage.topic=default.status
            key.converter=org.apache.kafka.connect.json.JsonConverter
            value.converter=org.apache.kafka.connect.json.JsonConverter
            internal.key.converter=org.apache.kafka.connect.json.JsonConverter
            internal.value.converter=org.apache.kafka.connect.json.JsonConverter



            internal.value.converter.schemas.enable=false
            internal.key.converter.schemas.enable=false
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_default_config_avro(self):
        self.is_connect_healthy_for_service("default-config-avro")
        props = self.cluster.run_command_on_service("default-config-avro", "cat /etc/kafka-connect/kafka-connect.properties")
        expected = """bootstrap.servers=kafka:9092
            rest.port=8082
            rest.advertised.host.name=default-config
            group.id=default
            config.storage.topic=default.config
            offset.storage.topic=default.offsets
            status.storage.topic=default.status
            key.converter=io.confluent.connect.avro.AvroConverter
            value.converter=io.confluent.connect.avro.AvroConverter
            internal.key.converter=org.apache.kafka.connect.json.JsonConverter
            internal.value.converter=org.apache.kafka.connect.json.JsonConverter



            value.converter.schema.registry.url=http://schema-registry:8081
            internal.value.converter.schemas.enable=false
            key.converter.schema.registry.url=http://schema-registry:8081
            internal.key.converter.schemas.enable=false
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_default_logging_config(self):
        self.is_connect_healthy_for_service("default-config")

        log4j_props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka/connect-log4j.properties")
        expected_log4j_props = """log4j.rootLogger=INFO, stdout

            log4j.appender.stdout=org.apache.log4j.ConsoleAppender
            log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
            log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n

            """
        self.assertEquals(log4j_props.translate(None, string.whitespace), expected_log4j_props.translate(None, string.whitespace))


def create_connector(name, create_command, host, port):

    utils.run_docker_command(
        image="confluentinc/cp-kafka-connect",
        command=create_command,
        host_config={'NetworkMode': 'host'})

    status = None
    for i in xrange(5):
        source_logs = utils.run_docker_command(
            image="confluentinc/cp-kafka-connect",
            command=CONNECTOR_STATUS.format(host=host, port=port, name=name),
            host_config={'NetworkMode': 'host'})

        connector = json.loads(source_logs)
        # Retry if you see errors, connect might still be creating the connector.
        if "error_code" in connector:
            time.sleep(5)
        else:
            status = connector["connector"]["state"]
            if status == "FAILED":
                return status
            elif status == "RUNNING":
                return status
            elif status == "UNASSIGNED":
                time.sleep(5)

    return status


def create_file_source_test_data(host_dir, file, num_records):
    volumes = []
    volumes.append("%s:/tmp/test" % host_dir)
    print "VOLUMES : ", volumes
    utils.run_docker_command(
        image="confluentinc/cp-kafka-connect",
        command="bash -c 'rm -rf /tmp/test/*.txt && seq {count} > /tmp/test/{name}'".format(count=num_records, name=file),
        host_config={'NetworkMode': 'host', 'Binds': volumes})


def wait_and_get_sink_output(host_dir, file, expected_num_records):
    volumes = []
    volumes.append("%s/:/tmp/test" % host_dir)
    for i in xrange(60):
        sink_record_count = utils.run_docker_command(
            image="confluentinc/cp-kafka-connect",
            command="bash -c '[ -e /tmp/test/%s ] && (wc -l /tmp/test/%s | cut -d\" \" -f1) || echo -1'" % (file, file),
            host_config={'NetworkMode': 'host', 'Binds': volumes})

        if int(sink_record_count.strip()) == expected_num_records:
            break
        time.sleep(10)

    return int(sink_record_count.strip())


class SingleNodeDistributedTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        machine_name = os.environ["DOCKER_MACHINE_NAME"]
        cls.machine = utils.TestMachine(machine_name)

        # Copy SSL files.
        cls.machine.ssh("mkdir -p /tmp/kafka-connect-single-node-test/jars")
        local_jars_dir = os.path.join(FIXTURES_DIR, "jars")
        cls.machine.scp_to_machine(local_jars_dir, "/tmp/kafka-connect-single-node-test")

        cls.machine.ssh("mkdir -p /tmp/kafka-connect-single-node-test/sql")
        local_sql_dir = os.path.join(FIXTURES_DIR, "sql")
        cls.machine.scp_to_machine(local_sql_dir, "/tmp/kafka-connect-single-node-test")

        cls.cluster = utils.TestCluster("distributed-single-node", FIXTURES_DIR, "distributed-single-node.yml")
        cls.cluster.start()
        # assert "PASS" in cls.cluster.run_command_on_service("zookeeper-bridge", ZK_READY.format(servers="localhost:2181"))
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-host", ZK_READY.format(servers="localhost:32181"))
        # assert "PASS" in cls.cluster.run_command_on_service("kafka-bridge", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-host", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("schema-registry-host", SR_READY.format(host="localhost", port="8081"))

    # @classmethod
    # def tearDownClass(cls):
    #     cls.machine.ssh("sudo rm -rf /tmp/kafka-connect-single-node-test")
    #     cls.cluster.shutdown()

    @classmethod
    def is_connect_healthy_for_service(cls, service, port):
        assert "PASS" in cls.cluster.run_command_on_service(service, CONNECT_HEALTH_CHECK.format(host="localhost", port=port))

    def create_topics(self, kafka_service, internal_topic_prefix, data_topic):
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".config"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".status"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".offsets"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=data_topic))

    def test_file_connector_on_host_network(self):

        # # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default", "one-node-file-test")
        # # Test from within the container
        self.is_connect_healthy_for_service("connect-host-json", 28082)

        # Create a file
        record_count = 10000
        create_file_source_test_data("/tmp/kafka-connect-single-node-test", "source.test.txt", record_count)

        file_source_create_cmd = FILE_SOURCE_CONNECTOR_CREATE % ("one-node-source-test", "one-node-file-test", "/tmp/test/source.test.txt", "localhost", "28082")
        source_status = create_connector("one-node-source-test", file_source_create_cmd, "localhost", "28082")
        self.assertEquals(source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % ("one-node-sink-test", "one-node-file-test", "/tmp/test/sink.test.txt", "localhost", "28082")
        sink_status = create_connector("one-node-sink-test", file_sink_create_cmd, "localhost", "28082")
        self.assertEquals(sink_status, "RUNNING")

        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", "sink.test.txt", record_count)
        self.assertEquals(sink_op, record_count)

    def test_file_connector_on_host_network_with_avro(self):

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default.avro", "one-node-avro-test")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-avro", 38082)

        # Create a file
        record_count = 10000
        create_file_source_test_data("/tmp/kafka-connect-single-node-test", "source.avro.test.txt", record_count)

        file_source_create_cmd = FILE_SOURCE_CONNECTOR_CREATE % ("one-node-source-test", "one-node-avro-test", "/tmp/test/source.avro.test.txt", "localhost", "38082")
        source_status = create_connector("one-node-source-test", file_source_create_cmd, "localhost", "38082")
        self.assertEquals(source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % ("one-node-sink-test", "one-node-avro-test", "/tmp/test/sink.avro.test.txt", "localhost", "38082")
        sink_status = create_connector("one-node-sink-test", file_sink_create_cmd, "localhost", "38082")
        self.assertEquals(sink_status, "RUNNING")

        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", "sink.avro.test.txt", record_count)
        self.assertEquals(sink_op, record_count)

    def test_jdbc_connector_on_host_network(self):

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default", "one-node-jdbc-test")

        assert "PASS" in self.cluster.run_command_on_service("mysql-host", "bash -c 'mysql -u root -pconfluent < /tmp/sql/mysql-test.sql && echo PASS'")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-json", 28082)

        jdbc_source_create_cmd = JDBC_SOURCE_CONNECTOR_CREATE % (
            "one-node-jdbc-test-source",
            "jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent",
            "one-node-jdbc-",
            "localhost",
            "28082")

        source_status = create_connector("one-node-jdbc-test-source", jdbc_source_create_cmd, "localhost", "28082")
        self.assertEquals(source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % ("one-node-sink-jdbc-test", "one-node-jdbc-test", "/tmp/test/sink.jdbc.test.txt", "localhost", "28082")
        sink_status = create_connector("one-node-sink-jdbc-test", file_sink_create_cmd, "localhost", "28082")
        self.assertEquals(sink_status, "RUNNING")

        record_count = 10
        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", "sink.jdbc.test.txt", record_count)
        self.assertEquals(sink_op, 10)

    def test_jdbc_connector_on_host_network_with_avro(self):

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default.avro", "one-node-jdbc-avro-test")

        assert "PASS" in self.cluster.run_command_on_service("mysql-host", "bash -c 'mysql -u root -pconfluent < /tmp/sql/mysql-test.sql && echo PASS'")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-avro", 38082)

        jdbc_source_create_cmd = JDBC_SOURCE_CONNECTOR_CREATE % (
            "one-node-jdbc-test-source",
            "jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent",
            "one-node-jdbc-avro-",
            "localhost",
            "38082")

        source_status = create_connector("one-node-jdbc-test-source", jdbc_source_create_cmd, "localhost", "38082")
        self.assertEquals(source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % ("one-node-sink-jdbc-test", "one-node-jdbc-avro-test", "/tmp/test/sink.jdbc.avro.test.txt", "localhost", "38082")
        sink_status = create_connector("one-node-sink-jdbc-test", file_sink_create_cmd, "localhost", "38082")
        self.assertEquals(sink_status, "RUNNING")

        record_count = 10
        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", "sink.jdbc.avro.test.txt", record_count)
        self.assertEquals(sink_op, 10)


class ClusterHostNetworkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        machine_name = os.environ["DOCKER_MACHINE_NAME"]
        cls.machine = utils.TestMachine(machine_name)

        # Copy SSL files.
        cls.machine.ssh("mkdir -p /tmp/kafka-connect-host-cluster-test/jars")
        local_jars_dir = os.path.join(FIXTURES_DIR, "jars")
        cls.machine.scp_to_machine(local_jars_dir, "/tmp/kafka-connect-host-cluster-test")
        cls.cluster = utils.TestCluster("cluster-test", FIXTURES_DIR, "cluster-host-plain.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-1", ZK_READY.format(servers="localhost:22181,localhost:32181,localhost:42181"))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-1", KAFKA_READY.format(brokers=3))

        # assert "PASS" in cls.cluster.run_command_on_service("schema-registry-1", SR_READY.format(host="localhost", port="8081"))

    @classmethod
    def tearDownClass(cls):
        cls.machine.ssh("sudo rm -rf /tmp/kafka-connect-host-cluster-test")
        cls.cluster.shutdown()

    def create_topics(self, kafka_service, internal_topic_prefix, data_topic):
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".config"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".status"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".offsets"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=data_topic))

    def test_cluster_running(self):
        self.assertTrue(self.cluster.is_running())

    @classmethod
    def is_connect_healthy_for_service(cls, service, port):
        assert "PASS" in cls.cluster.run_command_on_service(service, CONNECT_HEALTH_CHECK.format(host="localhost", port=port))

    def test_file_connector(self):

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-1", "default", "cluster-host-file-test")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-1", 28082)
        self.is_connect_healthy_for_service("connect-host-2", 38082)
        self.is_connect_healthy_for_service("connect-host-3", 48082)

        # Create a file
        record_count = 10000
        create_file_source_test_data("/tmp/connect-cluster-host-file-test", "source.test.txt", record_count)

        file_source_create_cmd = FILE_SOURCE_CONNECTOR_CREATE % ("cluster-host-source-test", "cluster-host-file-test", "/tmp/test/source.test.txt", "localhost", "28082")
        source_status = create_connector("cluster-host-source-test", file_source_create_cmd, "localhost", "28082")
        self.assertEquals(source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % ("cluster-host-sink-test", "cluster-host-file-test", "/tmp/test/sink.test.txt", "localhost", "38082")
        sink_status = create_connector("cluster-host-sink-test", file_sink_create_cmd, "localhost", "38082")
        self.assertEquals(sink_status, "RUNNING")

        sink_op = wait_and_get_sink_output("/tmp/connect-cluster-host-file-test", "sink.test.txt", record_count)
        self.assertEquals(sink_op, record_count)

    def test_file_connector_with_avro(self):

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-1", "default.avro", "cluster-host-avro-file-test")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-avro-1", 28083)
        self.is_connect_healthy_for_service("connect-host-avro-2", 38083)
        self.is_connect_healthy_for_service("connect-host-avro-3", 48083)

        # Create a file
        record_count = 10000
        create_file_source_test_data("/tmp/connect-cluster-host-file-test", "source.avro.test.txt", record_count)

        file_source_create_cmd = FILE_SOURCE_CONNECTOR_CREATE % ("cluster-host-source-test", "cluster-host-avro-file-test", "/tmp/test/source.avro.test.txt", "localhost", "28083")
        source_status = create_connector("cluster-host-source-test", file_source_create_cmd, "localhost", "28083")
        self.assertEquals(source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % ("cluster-host-sink-test", "cluster-host-avro-file-test", "/tmp/test/sink.avro.test.txt", "localhost", "38083")
        sink_status = create_connector("cluster-host-sink-test", file_sink_create_cmd, "localhost", "38083")
        self.assertEquals(sink_status, "RUNNING")

        sink_op = wait_and_get_sink_output("/tmp/connect-cluster-host-file-test", "sink.avro.test.txt", record_count)
        self.assertEquals(sink_op, record_count)
