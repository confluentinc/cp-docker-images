package io.confluent.admin.utils;

import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.common.utils.Utils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;

/**
 * Provides two commands:
 * <p/>
 * 1. zk-ready <connectString> <timeout> : This command checks if the zookeeper cluster
 * is ready to accept requests.
 * where:
 * <connectString> : Zookeeper connect string
 * <timeout> : timeout in millisecs for all operations .
 *
 * 2. kakfa-ready <path to client.properties> <minExpectedBrokers> <timeout> : This
 * command checks if the kafka cluster has the expected number of brokers and is ready to accept
 * requests.
 * where:
 * <path to client.properties> : path to properties with client config.
 * <minExpectedBrokers> : minimum brokers to wait for.
 * <timeout> : timeout in millisecs for all operations . Operations include waiting for Kafka
 * process to bind to the port, waiting for metadata request to return and waiting for
 * <minExpectedBrokers> to appear in the metadata.
 */
public class Main {

    private static final Logger log = LoggerFactory.getLogger(Main.class);

    public static void main(String[] args) {

        if (args.length == 0) {
            log.error("Usage : <command> <action> where action = kafka-ready or zk-ready>");
            System.exit(1);
        }

        if (args[0].equals("doc")) {
            KafkaMetadataClient.MetadataClientConfig.main(new String[]{});
        }

        boolean success = false;
        try {

            if (args[0].equals("zk-ready")) {
                if (args.length != 3) {
                    log.error("Usage : <command> zk-ready connect_string timeout");
                    System.exit(1);
                }
                String connectString = args[1];
                int timeOut = Integer.parseInt(args[2]);
                log.debug(connectString);
                success = ClusterStatus.isZookeeperReady(connectString, timeOut);
            } else if (args[0].equals("kafka-ready")) {
                if (args.length != 5) {
                    log.error("Usage : <command> kafka-ready bootstrap_broker_list path_to_client" +
                            ".properties min_brokers timeout ");
                    System.exit(1);
                }

                String bootStrapBrokersList = args[1];
                String metaDataClientProps = args[2];
                int minBrokers = Integer.parseInt(args[3]);
                int timeOut = Integer.parseInt(args[4]);
                Map<String, String> workerProps =
                        Utils.propsToStringMap(Utils.loadProps(metaDataClientProps));
                workerProps.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, bootStrapBrokersList);
                success = ClusterStatus.isKafkaReady(workerProps, minBrokers, timeOut);
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
