import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures", "debian", "kafka-connect")
KAFKA_READY = "bash -c 'cub kafka-ready {brokers} 40 -z $KAFKA_ZOOKEEPER_CONNECT && echo PASS || echo FAIL'"
CONNECT_HEALTH_CHECK = "bash -c 'dub wait {host} {port} 30 && curl -X GET --fail --silent {host}:{port}/connectors && echo PASS || echo FAIL'"
ZK_READY = "bash -c 'cub zk-ready {servers} 40 && echo PASS || echo FAIL'"
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

JDBC_SINK_CONNECTOR_CREATE = """
    curl -X POST -H "Content-Type: application/json" --data '{ "name": "%s", "config": { "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector", "tasks.max": 1, "connection.url": "%s", "topics": "%s", "auto.create": "true"}}' \
    http://%s:%s/connectors
"""

ES_SINK_CONNECTOR_CREATE = """
    curl -X POST -H "Content-Type: application/json" --data '{ "name": "%s", "config": { "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector", "tasks.max": 1, "connection.url": "%s", "topics": "%s", "key.ignore": "true", "type.name": "kafka-connect"}}' \
    http://%s:%s/connectors
"""

ACTIVEMQ_SOURCE_CONNECTOR_CREATE = """
    curl -X POST -H "Content-Type: application/json" --data '{ "name": "%s", "config": { "connector.class": "io.confluent.connect.jms.JmsSourceConnector", "tasks.max": 1, "activemq.url": "%s", "jms.destination.name": "testing", "kafka.topic": "%s", "confluent.topic.bootstrap.servers=": "%s"}}' \
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
        self.assertTrue("CONNECT_GROUP_ID is required." in self.cluster.service_logs("failing-config-group-id", stopped=True))
        self.assertTrue("CONNECT_CONFIG_STORAGE_TOPIC is required." in self.cluster.service_logs("failing-config-config-topic", stopped=True))
        self.assertTrue("CONNECT_OFFSET_STORAGE_TOPIC is required." in self.cluster.service_logs("failing-config-offset-topic", stopped=True))
        self.assertTrue("CONNECT_STATUS_STORAGE_TOPIC is required." in self.cluster.service_logs("failing-config-status-topic", stopped=True))
        self.assertTrue("CONNECT_KEY_CONVERTER is required." in self.cluster.service_logs("failing-config-key-converter", stopped=True))
        self.assertTrue("CONNECT_VALUE_CONVERTER is required." in self.cluster.service_logs("failing-config-value-converter", stopped=True))
        self.assertTrue("CONNECT_REST_ADVERTISED_HOST_NAME is required." in self.cluster.service_logs("failing-config-rest-adv-host-name", stopped=True))

    def test_default_config(self):
        self.is_connect_healthy_for_service("default-config")
        props = self.cluster.run_command_on_service("default-config", "bash -c 'cat /etc/kafka-connect/kafka-connect.properties | sort'")
        expected = """
            bootstrap.servers=kafka:9092
            config.storage.topic=default.config
            group.id=default
            internal.key.converter.schemas.enable=false
            internal.key.converter=org.apache.kafka.connect.json.JsonConverter
            internal.value.converter.schemas.enable=false
            internal.value.converter=org.apache.kafka.connect.json.JsonConverter
            key.converter=org.apache.kafka.connect.json.JsonConverter
            offset.storage.topic=default.offsets
            rest.advertised.host.name=default-config
            rest.port=8082
            status.storage.topic=default.status
            value.converter=org.apache.kafka.connect.json.JsonConverter
            zookeeper.connect=zookeeper:2181/defaultconfig
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_default_config_avro(self):
        self.is_connect_healthy_for_service("default-config-avro")
        props = self.cluster.run_command_on_service("default-config-avro", "bash -c 'cat /etc/kafka-connect/kafka-connect.properties | sort'")
        expected = """
            bootstrap.servers=kafka:9092
            config.storage.topic=default.config
            group.id=default
            internal.key.converter.schemas.enable=false
            internal.key.converter=org.apache.kafka.connect.json.JsonConverter
            internal.value.converter.schemas.enable=false
            internal.value.converter=org.apache.kafka.connect.json.JsonConverter
            key.converter.schema.registry.url=http://schema-registry:8081
            key.converter=io.confluent.connect.avro.AvroConverter
            offset.storage.topic=default.offsets
            rest.advertised.host.name=default-config
            rest.port=8082
            status.storage.topic=default.status
            value.converter.schema.registry.url=http://schema-registry:8081
            value.converter=io.confluent.connect.avro.AvroConverter
            zookeeper.connect=zookeeper:2181/defaultconfig
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_default_logging_config(self):
        self.is_connect_healthy_for_service("default-config")

        log4j_props = self.cluster.run_command_on_service("default-config", "bash -c 'cat /etc/kafka/connect-log4j.properties | sort'")
        expected_log4j_props = """
            log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n
            log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
            log4j.appender.stdout=org.apache.log4j.ConsoleAppender
            log4j.rootLogger=INFO, stdout
            """
        self.assertEquals(log4j_props.translate(None, string.whitespace), expected_log4j_props.translate(None, string.whitespace))


def create_connector(name, create_command, host, port):

    utils.run_docker_command(
        image="confluentinc/cp-kafka-connect",
        command=create_command,
        host_config={'NetworkMode': 'host'})

    status = None
    for i in xrange(25):
        source_logs = utils.run_docker_command(
            image="confluentinc/cp-kafka-connect",
            command=CONNECTOR_STATUS.format(host=host, port=port, name=name),
            host_config={'NetworkMode': 'host'})

        connector = json.loads(source_logs)
        # Retry if you see errors, connect might still be creating the connector.
        if "error_code" in connector:
            time.sleep(1)
        else:
            status = connector["connector"]["state"]
            if status == "FAILED":
                return status
            elif status == "RUNNING":
                return status
            elif status == "UNASSIGNED":
                time.sleep(1)

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
    # Polls the output of file sink and tries to wait until an expected no of records appear in the file.
    volumes = []
    volumes.append("%s/:/tmp/test" % host_dir)
    for i in xrange(60):
        sink_record_count = utils.run_docker_command(
            image="confluentinc/cp-kafka-connect",
            command="bash -c '[ -e /tmp/test/%s ] && (wc -l /tmp/test/%s | cut -d\" \" -f1) || echo -1'" % (file, file),
            host_config={'NetworkMode': 'host', 'Binds': volumes})

        # The bash command returns -1, if the file is not found. otherwise it returns the no of lines in the file.
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

        cls.machine.ssh("mkdir -p /tmp/kafka-connect-single-node-test/scripts")
        local_scripts_dir = os.path.join(FIXTURES_DIR, "scripts")
        cls.machine.scp_to_machine(local_scripts_dir, "/tmp/kafka-connect-single-node-test")

        cls.cluster = utils.TestCluster("distributed-single-node", FIXTURES_DIR, "distributed-single-node.yml")
        cls.cluster.start()
        # assert "PASS" in cls.cluster.run_command_on_service("zookeeper-bridge", ZK_READY.format(servers="localhost:2181"))
        assert "PASS" in cls.cluster.run_command_on_service("zookeeper-host", ZK_READY.format(servers="localhost:32181"))
        # assert "PASS" in cls.cluster.run_command_on_service("kafka-bridge", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-host", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("schema-registry-host", SR_READY.format(host="localhost", port="8081"))

    @classmethod
    def tearDownClass(cls):
        cls.machine.ssh("sudo rm -rf /tmp/kafka-connect-single-node-test")
        cls.cluster.shutdown()

    @classmethod
    def is_connect_healthy_for_service(cls, service, port):
        assert "PASS" in cls.cluster.run_command_on_service(service, CONNECT_HEALTH_CHECK.format(host="localhost", port=port))

    def create_topics(self, kafka_service, internal_topic_prefix, data_topic):
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".config"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".status"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=internal_topic_prefix + ".offsets"))
        assert "PASS" in self.cluster.run_command_on_service(kafka_service, TOPIC_CREATE.format(name=data_topic))

    def test_file_connector_on_host_network(self):

        data_topic = "one-node-file-test"
        file_source_input_file = "source.test.txt"
        file_sink_output_file = "sink.test.txt"
        source_connector_name = "one-node-source-test"
        sink_connector_name = "one-node-sink-test"
        worker_host = "localhost"
        worker_port = 28082

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default", data_topic)

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-json", 28082)

        # Create a file
        record_count = 10000
        create_file_source_test_data("/tmp/kafka-connect-single-node-test", file_source_input_file, record_count)

        file_source_create_cmd = FILE_SOURCE_CONNECTOR_CREATE % (source_connector_name, data_topic, "/tmp/test/%s" % file_source_input_file, worker_host, worker_port)
        source_status = create_connector(source_connector_name, file_source_create_cmd, worker_host, worker_port)
        self.assertEquals(source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % (sink_connector_name, data_topic, "/tmp/test/%s" % file_sink_output_file, worker_host, worker_port)
        sink_status = create_connector(sink_connector_name, file_sink_create_cmd, worker_host, worker_port)
        self.assertEquals(sink_status, "RUNNING")

        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", file_sink_output_file, record_count)
        self.assertEquals(sink_op, record_count)

    def test_file_connector_on_host_network_with_avro(self):

        data_topic = "one-node-avro-test"
        file_source_input_file = "source.avro.test.txt"
        file_sink_output_file = "sink.avro.test.txt"
        source_connector_name = "one-node-source-test"
        sink_connector_name = "one-node-sink-test"
        worker_host = "localhost"
        worker_port = 38082

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default.avro", data_topic)

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-avro", 38082)

        # Create a file
        record_count = 10000
        create_file_source_test_data("/tmp/kafka-connect-single-node-test", file_source_input_file, record_count)

        file_source_create_cmd = FILE_SOURCE_CONNECTOR_CREATE % (source_connector_name, data_topic, "/tmp/test/%s" % file_source_input_file, worker_host, worker_port)
        source_status = create_connector(source_connector_name, file_source_create_cmd, worker_host, worker_port)
        self.assertEquals(source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % (sink_connector_name, data_topic, "/tmp/test/%s" % file_sink_output_file, worker_host, worker_port)
        sink_status = create_connector(sink_connector_name, file_sink_create_cmd, worker_host, worker_port)
        self.assertEquals(sink_status, "RUNNING")

        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", file_sink_output_file, record_count)
        self.assertEquals(sink_op, record_count)

    def test_jdbc_source_connector_on_host_network(self):
        jdbc_topic_prefix = "one-node-jdbc-source-"
        data_topic = "%stest" % jdbc_topic_prefix
        file_sink_output_file = "file.sink.jdbcsource.test.txt"
        source_connector_name = "one-node-jdbc-source-test"
        sink_connector_name = "one-node-file-sink-test"
        worker_host = "localhost"
        worker_port = 28082

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default", data_topic)

        assert "PASS" in self.cluster.run_command_on_service("mysql-host", "bash -c 'mysql -u root -pconfluent < /tmp/sql/mysql-test.sql && echo PASS'")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-json", 28082)

        jdbc_source_create_cmd = JDBC_SOURCE_CONNECTOR_CREATE % (
            source_connector_name,
            "jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent",
            jdbc_topic_prefix,
            worker_host,
            worker_port)

        jdbc_source_status = create_connector(source_connector_name, jdbc_source_create_cmd, worker_host, worker_port)
        self.assertEquals(jdbc_source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % (
            sink_connector_name,
            data_topic,
            "/tmp/test/%s" % file_sink_output_file,
            worker_host,
            worker_port)
        sink_status = create_connector(sink_connector_name, file_sink_create_cmd, worker_host, worker_port)
        self.assertEquals(sink_status, "RUNNING")

        record_count = 10
        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", file_sink_output_file, record_count)
        self.assertEquals(sink_op, 10)

    def test_jdbc_source_connector_on_host_network_with_avro(self):

        jdbc_topic_prefix = "one-node-jdbc-source-avro-"
        data_topic = "%stest" % jdbc_topic_prefix
        file_sink_output_file = "file.sink.jdbcsource.avro.test.txt"
        source_connector_name = "one-node-jdbc-source-test"
        sink_connector_name = "one-node-file-sink-test"
        worker_host = "localhost"
        worker_port = 38082

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default.avro", data_topic)

        assert "PASS" in self.cluster.run_command_on_service("mysql-host", "bash -c 'mysql -u root -pconfluent < /tmp/sql/mysql-test.sql && echo PASS'")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-avro", 38082)

        jdbc_source_create_cmd = JDBC_SOURCE_CONNECTOR_CREATE % (
            source_connector_name,
            "jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent",
            jdbc_topic_prefix,
            worker_host,
            worker_port)

        jdbc_source_status = create_connector(source_connector_name, jdbc_source_create_cmd, worker_host, worker_port)
        self.assertEquals(jdbc_source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % (
            sink_connector_name,
            data_topic,
            "/tmp/test/%s" % file_sink_output_file,
            worker_host,
            worker_port)
        sink_status = create_connector(sink_connector_name, file_sink_create_cmd, worker_host, worker_port)
        self.assertEquals(sink_status, "RUNNING")

        record_count = 10
        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", file_sink_output_file, record_count)
        self.assertEquals(sink_op, 10)

    def test_jdbc_sink_connector_on_host_network_with_avro(self):

        topic = "test_jdbc_sink_avro"
        sink_connector_name = "one-node-jdbc-sink-test"
        worker_host = "localhost"
        worker_port = 38082

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default.avro", topic)

        # Create the database.
        assert "PASS" in self.cluster.run_command_on_service("mysql-host", "bash -c 'mysql -u root -pconfluent < /tmp/sql/mysql-test.sql && echo PASS'")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-avro", 38082)

        assert "PASS" in self.cluster.run_command_on_service("connect-host-avro", 'bash -c "TOPIC=%s sh /tmp/test/scripts/produce-data-avro.sh"' % topic)

        jdbc_sink_create_cmd = JDBC_SINK_CONNECTOR_CREATE % (
            sink_connector_name,
            "jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent",
            topic,
            worker_host,
            worker_port)

        jdbc_sink_status = create_connector(sink_connector_name, jdbc_sink_create_cmd, worker_host, worker_port)
        self.assertEquals(jdbc_sink_status, "RUNNING")

        assert "PASS" in self.cluster.run_command_on_service("mysql-host", """ bash -c "mysql --user=root --password=confluent --silent -e 'show databases;' | grep connect_test && echo PASS || echo FAIL" """)

        tmp = ""
        for i in xrange(25):
            if "PASS" in self.cluster.run_command_on_service("mysql-host", """ bash -c "mysql --user=root --password=confluent --silent --database=connect_test -e 'show tables;' | grep %s && echo PASS || echo FAIL" """ % topic):
                tmp = self.cluster.run_command_on_service("mysql-host", """ bash -c "mysql --user=root --password=confluent --silent --database=connect_test -e 'select COUNT(*) FROM %s ;' " """ % topic)
                if "10000" in tmp:
                    break

            time.sleep(1.0)

        assert "10000" in tmp

    def test_es_sink_connector_on_host_network_with_avro(self):

        topic = "test_es_sink_avro"
        sink_connector_name = "one-node-es-sink-test"
        worker_host = "localhost"
        worker_port = 38082

        self.create_topics("kafka-host", "default.avro", topic)

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-avro", 38082)

        assert "PASS" in self.cluster.run_command_on_service("connect-host-avro", 'bash -c "TOPIC=%s sh /tmp/test/scripts/produce-data-avro.sh"' % topic)

        es_sink_create_cmd = ES_SINK_CONNECTOR_CREATE % (
            sink_connector_name,
            "http://localhost:9200",
            topic,
            worker_host,
            worker_port)

        es_sink_status = create_connector(sink_connector_name, es_sink_create_cmd, worker_host, worker_port)
        self.assertEquals(es_sink_status, "RUNNING")

        tmp = ""
        for i in xrange(25):
            index_exists_cmd = 'bash -c "curl -s -f -XHEAD http://localhost:9200/%s && echo PASS || echo FAIL"' % topic
            if "PASS" in self.cluster.run_command_on_service("elasticsearch-host", index_exists_cmd):
                doc_count = """ bash -c "curl -s -f http://localhost:9200/_cat/count/%s | cut -d' ' -f3" """ % topic
                tmp = self.cluster.run_command_on_service("elasticsearch-host", doc_count)
                if "10000" in tmp:
                    break

            time.sleep(1.0)

        assert "10000" in tmp

    def test_activemq_source_connector_on_host_network_with_avro(self):

        activemq_topic_prefix = "one-node-activemq-source-avro-"
        data_topic = "%stest" % activemq_topic_prefix
        source_connector_name = "one-node-activemq-source-test"
        sink_connector_name = "one-node-activemq-file-sink-test"
        worker_host = "localhost"
        worker_port = 38082

        # Creating topics upfront makes the tests go a lot faster (I suspect this is because consumers dont waste time with rebalances)
        self.create_topics("kafka-host", "default.avro", data_topic)

        assert "PASS" in self.cluster.run_command_on_service("activemq-host", "bash -c 'bin/activemq producer --message MyMessage --messageCount 1000 --destination queue://TEST' | grep 'Produced: 1000 messages' && echo PASS || echo FAIL")

        # Test from within the container
        self.is_connect_healthy_for_service("connect-host-avro", 38082)

        activemq_source_create_cmd = ACTIVEMQ_SOURCE_CONNECTOR_CREATE % (
            source_connector_name,
            "tcp://127.0.0.1:61616",
            data_topic,
            "localhost:9092",
            worker_host,
            worker_port)

        activemq_source_status = create_connector(source_connector_name, activemq_source_create_cmd, worker_host, worker_port)
        self.assertEquals(activemq_source_status, "RUNNING")

        file_sink_create_cmd = FILE_SINK_CONNECTOR_CREATE % (
            sink_connector_name,
            data_topic,
            "/tmp/test/%s" % file_sink_output_file,
            worker_host,
            worker_port)
        sink_status = create_connector(sink_connector_name, file_sink_create_cmd, worker_host, worker_port)
        self.assertEquals(sink_status, "RUNNING")

        record_count = 1000
        sink_op = wait_and_get_sink_output("/tmp/kafka-connect-single-node-test", file_sink_output_file, record_count)
        self.assertEquals(sink_op, 1000)


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
