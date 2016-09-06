package io.confluent.admin.utils.cli;

import io.confluent.admin.utils.ClusterStatus;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.MutuallyExclusiveGroup;
import net.sourceforge.argparse4j.inf.Namespace;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.common.utils.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;

import static net.sourceforge.argparse4j.impl.Arguments.store;

/**
 * This command checks if the kafka cluster has the expected number of brokers and is ready to accept
 * requests.
 * where:
 * <config>                 : path to properties with client config.
 * <min-expected-brokers>   : minimum brokers to wait for.
 * <timeout>                : timeout in ms for all operations. This includes looking up metadata in Zookeeper
 *                            or fetching metadata for the brokers.
 * (<bootstrap-brokers>
 *     or
 * <zookeeper-connect>)     : Either a bootstrap broker list or zookeeper connect string
 * <security-protocol>      : Security protocol to use to connect to the broker.
 */
public class KafkaReadyCommand {

    private static final Logger log = LoggerFactory.getLogger(KafkaReadyCommand.class);
    public static final String KAFKA_READY = "kafka-ready";

    private static ArgumentParser createArgsParser() {
        ArgumentParser kafkaReady = ArgumentParsers
                .newArgumentParser(KAFKA_READY)
                .defaultHelp(true)
                .description("Check if Kafka is ready.");

        kafkaReady.addArgument("min-expected-brokers")
                .action(store())
                .required(true)
                .type(Integer.class)
                .metavar("MIN_EXPECTED_BROKERS")
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
        kafkaOrZK.addArgument("--bootstrap-servers", "-b")
                .action(store())
                .type(String.class)
                .metavar("BOOTSTRAP_SERVERS")
                .help("List of bootstrap brokers.");

        kafkaOrZK.addArgument("--zookeeper-connect", "-z")
                .action(store())
                .type(String.class)
                .metavar("ZOOKEEPER_CONNECT")
                .help("Zookeeper connect string.");

        kafkaReady.addArgument("--security-protocol", "-s")
                .action(store())
                .type(String.class)
                .metavar("SECURITY_PROTOCOL")
                .setDefault("PLAINTEXT")
                .help("Which endpoint to connect to ? ");


        return kafkaReady;
    }

    public static void main(String[] args) {

        ArgumentParser parser = createArgsParser();
        boolean success = false;
        try {
            Namespace res = parser.parseArgs(args);
            log.debug("Arguments {}. ", res);

            Map<String, String> workerProps = new HashMap<>();

            if (res.getString("config") == null &&
                    !(res.getString("security_protocol").equals("PLAINTEXT"))) {
                log.error("config is required for all protocols except PLAINTEXT");
                success = false;
            } else {
                if (res.getString("config") != null) {
                    workerProps = Utils.propsToStringMap(Utils.loadProps(res.getString("config")));
                }
                if (res.getString("bootstrap_servers") != null) {
                    workerProps.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG,
                            res.getString("bootstrap_servers"));
                } else {
                    String zkConnectString = res.getString("zookeeper_connect");
                    boolean zkReady = ClusterStatus.isZookeeperReady(zkConnectString, res.getInt("timeout"));
                    if (!zkReady) {
                        throw new RuntimeException("Could not reach zookeeper " + zkConnectString);
                    }
                    Map<String, String> endpoints = ClusterStatus.getKafkaEndpointFromZookeeper(
                            zkConnectString,
                            res.getInt("timeout"));

                    String bootstrap_broker = endpoints.get(res.getString("security_protocol"));
                    workerProps.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, bootstrap_broker);

                }
                success = ClusterStatus.isKafkaReady(workerProps,
                        res.getInt("min_expected_brokers"),
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
            log.error("Error while running kafka-ready.", e);
            success = false;
        }

        if (success) {
            System.exit(0);
        } else {
            System.exit(1);
        }
    }
}
