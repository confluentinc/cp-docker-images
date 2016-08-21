package io.confluent.admin.utils;

import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.*;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.common.utils.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;

import static net.sourceforge.argparse4j.impl.Arguments.store;

/**
 * Provides two commands:
 * <p/>
 * 1. zk-ready <connectString> <timeout>
 * This command checks if the zookeeper cluster is ready to accept requests.
 * where:
 * <connectString> : Zookeeper connect string
 * <timeout> : timeout in millisecs for all operations .
 * <p>
 *
 * 2. kakfa-ready <minExpectedBrokers> <timeout> (<broker_list>or <zookeeper_connect>) <config> <security_protocol>
 * This command checks if the kafka cluster has the expected number of brokers and is ready to accept
 * requests.
 * where:
 * <config> : path to properties with client config.
 * <minExpectedBrokers> : minimum brokers to wait for.
 * <timeout> : timeout in millisecs for all operations . Operations include waiting for Kafka
 * process to bind to the port, waiting for metadata request to return and waiting for
 * <minExpectedBrokers> to appear in the metadata.
 * (<broker_list>or <zookeeper_connect>) : Either a bootstrap broker list or zookeeper connect string
 * security_protocol : Security protocol to use to connect to the broker.
 */
public class Main {

    private static final Logger log = LoggerFactory.getLogger(Main.class);

    private static ArgumentParser createArgsParser() {
        ArgumentParser root = ArgumentParsers
                .newArgumentParser("cub")
                .defaultHelp(true)
                .description("Confluent Platform Utility Belt.");

        Subparser kafkaReady = root.addSubparsers()
                .dest("name")
                .addParser("kafka-ready")
                .description("Check if Kafka is ready.");

        kafkaReady.addArgument("expected-brokers")
                .action(store())
                .required(true)
                .type(Integer.class)
                .metavar("EXPECTED_BROKERS")
                .help("Minimum number of brokers to wait for.");

        kafkaReady.addArgument("timeout")
                .action(store())
                .required(true)
                .type(Integer.class)
                .metavar("TIMEOUT_IN_MS")
                .help("Time (in ms) to wait for service to be ready.");

        kafkaReady.addArgument("--config", "-c")
                .action(store())
                .type(String.class)
                .metavar("CONFIG")
                .help("List of bootstrap brokers.");

        MutuallyExclusiveGroup kafkaOrZK = kafkaReady.addMutuallyExclusiveGroup();
        kafkaOrZK.addArgument("--bootstrap-broker-list", "-b")
                .action(store())
                .type(String.class)
                .metavar("BOOTSTRAP_BROKER_LIST")
                .help("List of bootstrap brokers.");

        kafkaOrZK.addArgument("--zookeeper-connect", "-z")
                .action(store())
                .type(String.class)
                .metavar("ZOOKEEPER_CONNECT_STRING")
                .help("Zookeeper connect string.");

        kafkaReady.addArgument("--security-protocol", "-s")
                .action(store())
                .type(String.class)
                .metavar("SECURITY_PROTOCOL")
                .setDefault("PLAINTEXT")
                .help("Which endpoint to connect to ? ");

        Subparser zkReady = root.addSubparsers()
                .dest("name")
                .addParser("zk-ready")
                .description("Check if ZK is ready.");

        zkReady.addArgument("connect_string")
                .action(store())
                .required(true)
                .type(String.class)
                .metavar("CONNECT_STRING")
                .help("Zookeeper connect string.");

        zkReady.addArgument("timeout")
                .action(store())
                .required(true)
                .type(Integer.class)
                .metavar("TIMEOUT IN MS")
                .help("Time (in ms) to wait for service to be ready.");

        Subparser doc = root.addSubparsers()
                .dest("name")
                .addParser("doc")
                .description("Print config docs in HTML.");

        return root;
    }

    public static void main(String[] args) {

        ArgumentParser parser = createArgsParser();
        boolean success = false;
        try {
            Namespace res = parser.parseArgs(args);
            String command = res.getString("name");
            log.debug("Args: " + res);

            if (command.equals("doc")) {
                KafkaMetadataClient.MetadataClientConfig.main(new String[]{});
                success = true;
            } else if (command.equals("zk-ready")) {
                success = ClusterStatus.isZookeeperReady(
                        res.getString("connect_string"),
                        res.getInt("timeout"));
            } else if (command.equals("kafka-ready")) {

                Map<String, String> workerProps = new HashMap<>();

                if (res.getString("config") == null &&
                        !(res.getString("security_protocol").equals("PLAINTEXT"))) {
                    throw new IllegalArgumentException("config is required for all protocols except PLAINTEXT");
                }

                if (res.getString("config") != null) {
                    workerProps = Utils.propsToStringMap(Utils.loadProps(res.getString("config")));
                }
                if (res.getString("bootstrap_broker_list") != null) {
                    workerProps.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG,
                            res.getString("bootstrap_broker_list"));
                } else {
                    String zkConnectString = res.getString("zookeeper_connect");
                    boolean zkReady = ClusterStatus.isZookeeperReady(zkConnectString, res.getInt("timeout"));
                    if (! zkReady) {
                        throw new RuntimeException("Could not reach zookeeper " + zkConnectString);
                    }
                    Map<String, String> endpoints = ClusterStatus.getKafkaEndpointFromZookeeper(
                            zkConnectString,
                            res.getInt("timeout"));

                    String bootstrap_broker = endpoints.get(res.getString("security_protocol"));
                    workerProps.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, bootstrap_broker);

                }
                success = ClusterStatus.isKafkaReady(workerProps,
                        res.getInt("expected_brokers"),
                        res.getInt("timeout"));
            }

        } catch (ArgumentParserException e) {
            if (args.length == 0) {
                parser.printHelp();
                success = true;
            } else {
                parser.handleError(e);
                success = false;
            }
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            success = false;
        }

        if (success) {
            System.exit(0);
        } else {
            System.exit(1);
        }
    }
}
