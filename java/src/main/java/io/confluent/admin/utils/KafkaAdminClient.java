package io.confluent.admin.utils;

import org.apache.kafka.clients.ClientResponse;
import org.apache.kafka.clients.ClientUtils;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.Metadata;
import org.apache.kafka.clients.NetworkClient;
import org.apache.kafka.clients.consumer.internals.ConsumerNetworkClient;
import org.apache.kafka.clients.consumer.internals.RequestFuture;
import org.apache.kafka.common.Cluster;
import org.apache.kafka.common.Node;
import org.apache.kafka.common.config.AbstractConfig;
import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.common.metrics.Metrics;
import org.apache.kafka.common.network.ChannelBuilder;
import org.apache.kafka.common.network.Selector;
import org.apache.kafka.common.requests.AbstractRequest;
import org.apache.kafka.common.requests.AbstractResponse;
import org.apache.kafka.common.requests.MetadataRequest;
import org.apache.kafka.common.requests.MetadataResponse;
import org.apache.kafka.common.utils.SystemTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.InetSocketAddress;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * This is a partial Java port of
 * https://github.com/apache/kafka/blob/trunk/core/src/main/scala/kafka/admin/AdminClient.scala
 */

public class KafkaAdminClient {

    private static final Logger log = LoggerFactory.getLogger(KafkaAdminClient.class);
    private static final AtomicInteger adminClientIdSequence = new AtomicInteger(1);
    private final ConsumerNetworkClient client;
    private final SystemTime time;
    private final List<InetSocketAddress> brokerAddresses;
    private final List<Node> bootStrapBrokers;
    private final Long maxPollTimeoutMs;


    public KafkaAdminClient(Map<String, String> config) {

        MetadataClientConfig adminCfg = new MetadataClientConfig(config);
        time = new SystemTime();
        Metrics metrics = new Metrics(time);
        Metadata metadata = new Metadata();
        ChannelBuilder channelBuilder = ClientUtils.createChannelBuilder(adminCfg.values());

        List<String> brokerUrls = adminCfg.getList(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG);
        brokerAddresses = ClientUtils.parseAndValidateAddresses(brokerUrls);
        Cluster bootstrapCluster = Cluster.bootstrap(brokerAddresses);
        metadata.update(bootstrapCluster, 0);

        Selector selector = new Selector(MetadataClientConfig.defaultConnectionMaxIdleMs,
                metrics,
                time,
                "admin",
                channelBuilder);

        NetworkClient networkClient = new NetworkClient(selector, metadata,
            "admin-" + adminClientIdSequence.getAndIncrement(),
            MetadataClientConfig.defaultMaxInFlightRequestsPerConnection,
            MetadataClientConfig.defaultReconnectBackoffMs,
            MetadataClientConfig.defaultSendBufferBytes,
            MetadataClientConfig.defaultReceiveBufferBytes,
            MetadataClientConfig.defaultRequestTimeoutMs,
            time,
            true);

        client = new ConsumerNetworkClient(networkClient,
                metadata,
                time,
                MetadataClientConfig.defaultRetryBackoffMs,
                MetadataClientConfig.defaultRequestTimeoutMs);

        this.bootStrapBrokers = bootstrapCluster.nodes();
        this.maxPollTimeoutMs = adminCfg.getLong(MetadataClientConfig.MAX_POLL_TIMEOUT_MS_CONFIG);

    }

    public List<InetSocketAddress> getBrokerAddresses() {
        return brokerAddresses;
    }

    public List<Node> findAllBrokers(long timeoutMs) {
        MetadataResponse response = getMetadataResponse(timeoutMs);

        if (response == null) {
          return null;
        }

        return response.cluster().nodes();
    }

    private MetadataResponse getMetadataResponse(long timeoutMs) {
        MetadataRequest.Builder request = new MetadataRequest.Builder(Collections.emptyList());
        return (MetadataResponse) sendAnyNode(request, timeoutMs);
    }


    private AbstractResponse sendAnyNode(AbstractRequest.Builder request, long timeoutMs) {
        for (Node broker : this.bootStrapBrokers) {
            try {
                return send(broker, request, timeoutMs);
            } catch (Exception e) {
                log.error("Request {} failed against node {}.", request, broker, e);
            }
        }
        log.error("Request {} failed on all bootstrap brokers {}.", request, this.bootStrapBrokers);
        return null;
    }

    private AbstractResponse send(Node target, AbstractRequest.Builder request) {
      return send(target, request, this.maxPollTimeoutMs);
    }

    private AbstractResponse send(Node target, AbstractRequest.Builder request, long timeoutMs) {
        log.trace("Sending request (" + request.toString() + ") to node " + target.toString());
        RequestFuture<ClientResponse> future = client.send(target, request);
        client.poll(future, timeoutMs );

        if (future.succeeded()) {
            log.trace("Received response (" + future.value().responseBody() + ")");
            return future.value().responseBody();
        } else {
            log.trace("Future failed with exception: " + future.exception().getMessage());
            throw future.exception();
        }
    }

    public static class MetadataClientConfig extends AbstractConfig {

        public static final String MAX_POLL_TIMEOUT_MS_CONFIG = "max.poll.timeout.ms";
        public static final String MAX_POLL_TIMEOUT_MS_DOC = "The maximum time to wait for a request";
        public static final long defaultMaxPollTimeoutMs = 5000L;

        private static final int defaultConnectionMaxIdleMs = 9 * 60 * 1000;
        private static final int defaultRequestTimeoutMs = 5000;
        private static final int defaultMaxInFlightRequestsPerConnection = 100;
        private static final int defaultReconnectBackoffMs = 50;
        private static final int defaultSendBufferBytes = 128 * 1024;
        private static final int defaultReceiveBufferBytes = 32 * 1024;
        private static final int defaultRetryBackoffMs = 100;
        private static final ConfigDef CONFIG;

        static {
            CONFIG = new ConfigDef()
                .define(
                    MAX_POLL_TIMEOUT_MS_CONFIG,
                    ConfigDef.Type.LONG,
                    defaultMaxPollTimeoutMs,
                    ConfigDef.Importance.MEDIUM,
                    MAX_POLL_TIMEOUT_MS_DOC)
                    .define(
                            CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG,
                            ConfigDef.Type.LIST,
                            ConfigDef.Importance.HIGH,
                            CommonClientConfigs.BOOSTRAP_SERVERS_DOC)
                    .define(
                            CommonClientConfigs.SECURITY_PROTOCOL_CONFIG,
                            ConfigDef.Type.STRING,
                            CommonClientConfigs.DEFAULT_SECURITY_PROTOCOL,
                            ConfigDef.Importance.MEDIUM,
                            CommonClientConfigs.SECURITY_PROTOCOL_DOC)
                    .withClientSslSupport()
                    .withClientSaslSupport();
        }

        public MetadataClientConfig(Map<?, ?> props) {
            super(CONFIG, props, true);
        }

        public static void main(String[] args) {
            System.out.println(CONFIG.toHtmlTable());
        }

    }

}
