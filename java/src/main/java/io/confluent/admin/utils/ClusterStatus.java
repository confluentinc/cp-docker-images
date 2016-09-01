/**
 * Copyright 2016 Confluent Inc.
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * http://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package io.confluent.admin.utils;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import org.apache.kafka.common.Node;
import org.apache.kafka.common.errors.TimeoutException;
import org.apache.zookeeper.KeeperException;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.ZooKeeper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static org.apache.kafka.common.utils.Utils.sleep;

/**
 * Checks status of Zookeeper / Kafka cluster.
 */
public class ClusterStatus {

    private static final Logger log = LoggerFactory.getLogger(ClusterStatus.class);
    public static final String JAVA_SECURITY_AUTH_LOGIN_CONFIG = "java.security.auth.login.config";
    public static final String BROKERS_IDS_PATH = "/brokers/ids";
    public static final int BROKER_METADATA_REQUEST_BACKOFF_MS = 1000;

    /**
     * Checks if the zookeeper cluster is ready to accept requests.
     *
     * @param zkConnectString Zookeeper connect string
     * @param timeoutMs       timeoutMs in milliseconds
     * @return true if the cluster is ready, false otherwise.
     */
    public static boolean isZookeeperReady(String zkConnectString, int timeoutMs) {
        log.debug("Check if Zookeeper is ready: {} ", zkConnectString);
        ZooKeeper zookeeper = null;
        try {

            CountDownLatch waitForConnection = new CountDownLatch(1);

            boolean isSASLEnabled = false;
            if (System.getProperty(JAVA_SECURITY_AUTH_LOGIN_CONFIG, null) != null) {
                isSASLEnabled = true;
                log.info("SASL is enabled. java.security.auth.login.config={}",
                        System.getProperty(JAVA_SECURITY_AUTH_LOGIN_CONFIG));
            }
            ZookeeperConnectionWatcher connectionWatcher =
                    new ZookeeperConnectionWatcher(waitForConnection, isSASLEnabled);
            zookeeper = new ZooKeeper(zkConnectString, timeoutMs, connectionWatcher);

            boolean timedOut = !waitForConnection.await(timeoutMs, TimeUnit.MILLISECONDS);
            if (timedOut) {
                log.error("Timed out waiting for connection to Zookeeper server [{}].",
                        zkConnectString);
                return false;
            } else if (!connectionWatcher.isSuccessful()) {
                log.error("Error occurred while connecting to Zookeeper server[{}]. {} ",
                        zkConnectString,
                        connectionWatcher.getFailureMessage());
                return false;
            } else {
                return true;
            }
        } catch (Exception e) {
            log.error("Error while waiting for Zookeeper client to connect to the server [{}].",
                    zkConnectString, e);
            return false;
        } finally {
            if (zookeeper != null) {
                try {
                    zookeeper.close();
                } catch (InterruptedException e) {
                    log.error("Error while shutting down Zookeeper client.", e);
                    Thread.currentThread().interrupt();
                }
            }
        }
    }

    /**
     * Checks if the kafka cluster is accepting client requests and
     * has at least minBrokerCount brokers.
     *
     * @param minBrokerCount Expected no of brokers
     * @param timeoutMs      timeoutMs in milliseconds
     * @return true is the cluster is ready, false otherwise.
     */
    public static boolean isKafkaReady(Map<String, String> config, int
            minBrokerCount, int timeoutMs) {

        log.debug("Check if Kafka is ready: {}", config);
        KafkaAdminClient adminClient = new KafkaAdminClient(config);

        long begin = System.currentTimeMillis();
        long remainingWaitMs = timeoutMs;
        List<Node> brokers = new ArrayList<>();
        while (remainingWaitMs > 0) {

            // The metadata query doesnot wait for all brokers to be ready before
            // returning the brokers. So, wait until expected brokers are present
            // or the time out expires.
            try {
                brokers = adminClient.findAllBrokers((int) remainingWaitMs);
                log.debug("Broker list: {}", (brokers != null ? brokers : "[]"));
                if ((brokers != null) && (brokers.size() >= minBrokerCount)) {
                    return true;
                }
            } catch (Exception e) {
                log.error("Error while getting broker list.", e);
                // Swallow exceptions because we want to retry until timeoutMs expires.
            }

            sleep(Math.min(BROKER_METADATA_REQUEST_BACKOFF_MS, remainingWaitMs));

            log.info("Expected {} brokers but found only {}. Trying to query Kafka for metadata again ...",
                    minBrokerCount,
                    brokers == null ? 0 : brokers.size());
            long elapsed = System.currentTimeMillis() - begin;
            remainingWaitMs = timeoutMs - elapsed;
        }

        log.error("Expected {} brokers but found only {}. Brokers found {}.",
                minBrokerCount,
                brokers == null ? 0 : brokers.size(),
                brokers != null ? brokers : "[]");

        return false;
    }

    /**
     * Gets metadata from Zookeeper. This method only waits for at least one broker to be present.
     *
     * @param zkConnectString Zookeeper connect string
     * @param timeoutMs       Timeout in milliseconds
     * @return A list of broker metadata with at least one broker.
     * @throws KeeperException
     * @throws InterruptedException
     * @throws IOException
     */
    private static List<String> getBrokerMetadataFromZookeeper(String zkConnectString, int
            timeoutMs) throws KeeperException, InterruptedException, IOException {
        log.debug("Get a bootstrap broker from Zookeeper [{}].", zkConnectString);
        ZooKeeper zookeeper = null;
        try {

            zookeeper = createZookeeperClient(zkConnectString, timeoutMs);
            boolean isBrokerRegisted = isKafkaRegisteredInZookeeper(zookeeper, timeoutMs);

            if (!isBrokerRegisted) {
                return Collections.emptyList();
            }
            final List<String> brokers = getRawKafkaMetadataFromZK(zookeeper, timeoutMs);

            // Get metadata for brokers.
            List<String> brokerMetadata = new ArrayList<>();
            for (String broker : brokers) {
                String brokerIdPath = String.format("%s/%s", BROKERS_IDS_PATH, broker);
                brokerMetadata.add(new String(zookeeper.getData(brokerIdPath, false, null)));
            }
            return brokerMetadata;
        } finally {
            if (zookeeper != null) {
                try {
                    zookeeper.close();
                } catch (InterruptedException e) {
                    log.error("Error while shutting down Zookeeper client.", e);
                    Thread.currentThread().interrupt();
                }
            }
        }
    }

    /**
     * Gets raw Kafka metadata from Zookeeper.
     * @param timeoutMs timeout in ms.
     * @param zookeeper Zookeeper client.
     * @return List of Kafka metadata strings.
     * @throws InterruptedException
     * @throws KeeperException
     */
    private static List<String> getRawKafkaMetadataFromZK(ZooKeeper zookeeper, int timeoutMs)
            throws InterruptedException, KeeperException {
        // Get the data.
        CountDownLatch waitForBroker = new CountDownLatch(1);

        // Get children async. Countdown when one of the following happen:
        // 1. NodeChildrenChanged is triggered (this happens when children are created after the call is made).
        // 2. ChildrenCallback gets a callback with children present (this happens when node has
        //    children when the call is made) .
        final List<String> brokers = new CopyOnWriteArrayList<>();
        zookeeper.getChildren(BROKERS_IDS_PATH,
                (event) -> {
                    log.debug("Got event when checking for children of /brokers/ids. type={} path={}",
                            event.getType(), event.getPath());
                    if (event.getType() == Watcher.Event.EventType.NodeChildrenChanged) {
                        waitForBroker.countDown();
                    }
                },
                (rc, path, ctx, children) -> {
                    log.debug("ChildrenCallback got data for path={} children={}", path, children);
                    if (children != null && children.size() > 0) {
                        children.addAll(brokers);
                        waitForBroker.countDown();
                    }
                },
                null);


        boolean waitForBrokerTimedOut = !waitForBroker.await(timeoutMs, TimeUnit.MILLISECONDS);
        if (waitForBrokerTimedOut) {
            String message = String.format("Timed out waiting for Kafka to register brokers in Zookeeper. " +
                            "timeout (ms) = %s", timeoutMs);
            throw new TimeoutException(message);
        }


        if (brokers.isEmpty()) {
            // Get children. Broker list will be empty if the getChildren call above is made before the children are
            // present. In that case, the ChildrenCallback will be called with an empty children list and we will wait
            // for the NodeChildren event to be fired. At this point, this has happened and we can the children
            // safely using a sync call.
            zookeeper.getChildren(BROKERS_IDS_PATH, false, null).forEach((child) -> brokers.add(child));
        }
        return brokers;
    }

    /**
     * Checks whether /brokers/ids is present. This signifies that at least one Kafka broker has
     * registered in ZK.
     * @param timeoutMs timeout in ms.
     * @param zookeeper Zookeeper client.
     * @return True if /brokers/ids is present.
     * @throws InterruptedException
     */
    private static boolean isKafkaRegisteredInZookeeper(ZooKeeper zookeeper, int timeoutMs)
            throws InterruptedException {
        // Make sure /brokers/ids exists. Countdown when one of the following happen:
        // 1. node created event is triggered (this happens when /brokers/ids is created after the call is made).
        // 2. StatCallback gets a non-null callback (this happens when /brokers/ids exists when the call is made) .
        CountDownLatch kafkaRegistrationSignal = new CountDownLatch(1);
        zookeeper.exists(BROKERS_IDS_PATH,
                (event) -> {
                    log.debug("Got event when checking for existence of /brokers/ids. type={} path={}"
                            , event.getType(), event.getPath());
                    if (event.getType() == Watcher.Event.EventType.NodeCreated) {
                        kafkaRegistrationSignal.countDown();
                    }
                },
                (rc, path, ctx, stat) -> {
                    log.debug("StatsCallback got data for path={}, stat={}", path, stat);
                    if (stat != null) {
                        kafkaRegistrationSignal.countDown();
                    }
                },
                null);

        boolean kafkaRegistrationTimedOut = !kafkaRegistrationSignal.await(
                timeoutMs,
                TimeUnit.MILLISECONDS);
        if (kafkaRegistrationTimedOut) {
            String message = String.format("Timed out waiting for Kafka to create /brokers/ids in Zookeeper. " +
                            "timeout (ms) = %s", timeoutMs);
            throw new TimeoutException(message);
        }

        return true;
    }

    /**
     * Create a Zookeeper Client.
     * @param zkConnectString Zookeeper connect string.
     * @param timeoutMs timeout in ms.
     * @return Zookeeper Client.
     * @throws IOException
     * @throws InterruptedException
     */
    private static ZooKeeper createZookeeperClient(String zkConnectString, int timeoutMs)
            throws IOException, InterruptedException {

        CountDownLatch waitForConnection = new CountDownLatch(1);
        ZooKeeper zookeeper;
        boolean isSASLEnabled = false;
        if (System.getProperty(JAVA_SECURITY_AUTH_LOGIN_CONFIG, null) != null) {
            isSASLEnabled = true;
        }
        ZookeeperConnectionWatcher connectionWatcher =
                new ZookeeperConnectionWatcher(waitForConnection, isSASLEnabled);
        int zkSessionTimeoutMs = timeoutMs;
        zookeeper = new ZooKeeper(zkConnectString, zkSessionTimeoutMs, connectionWatcher);

        boolean timedOut = !waitForConnection.await(timeoutMs, TimeUnit.MILLISECONDS);
        if (timedOut) {
            String message = String.format("Timed out waiting for connection to Zookeeper. " +
                            "timeout (ms) = %s, Zookeeper connect = %s",
                    timeoutMs,
                    zkConnectString);
            throw new TimeoutException(message);
        } else if (!connectionWatcher.isSuccessful()) {
            String message = String.format("Error occurred while connecting to Zookeeper server [%s]. %s",
                    zkConnectString,
                    connectionWatcher.getFailureMessage());
            throw new RuntimeException(message);
        }
        return zookeeper;
    }

    /**
     * Gets a kafka endpoint for one broker from Zookeeper. This method is used to get a broker for the
     * bootstrap broker list. This method is expected to used in conjunction with isKafkaReady to
     * determine if Kafka is ready.
     *
     * @param zkConnectString Zookeeper connect string
     * @param timeoutMs       Timeout in milliseconds
     * @return A map of security-protocol->endpoints
     * @throws InterruptedException
     * @throws IOException
     * @throws KeeperException
     */
    public static Map<String, String> getKafkaEndpointFromZookeeper(
            String zkConnectString,
            int timeoutMs) throws InterruptedException, IOException, KeeperException {

        List<String> brokerMetadata = getBrokerMetadataFromZookeeper(zkConnectString, timeoutMs);

        // Get the first broker. We will use this as the bootstrap broker for isKafkaReady method.
        if (brokerMetadata.isEmpty()) {
            throw new RuntimeException("No brokers found in Zookeeper [" + zkConnectString + "] .");
        }
        String broker = brokerMetadata.get(0);

        Map<String, String> endpointMap = new HashMap<>();
        Gson gson = new Gson();
        Type type = new TypeToken<Map<String, Object>>() {}.getType();
        Map<String, Object> parsedBroker = gson.fromJson(broker, type);

        for (String rawEndpoint : (List<String>) parsedBroker.get("endpoints")) {
            String[] protocolAddress = rawEndpoint.split("://");

            String protocol = protocolAddress[0];
            String address = protocolAddress[1];
            endpointMap.put(protocol, address);
        }
        return endpointMap;
    }
}
