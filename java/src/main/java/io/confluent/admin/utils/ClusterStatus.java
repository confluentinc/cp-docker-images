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
import org.apache.kafka.common.utils.SystemTime;
import org.apache.kafka.common.utils.Time;
import org.apache.zookeeper.KeeperException;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.client.ConnectStringParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.lang.reflect.Type;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/**
 * Checks status of Zookeeper / Kafka cluster.
 */
public class ClusterStatus {
    private static final Logger log = LoggerFactory.getLogger(ClusterStatus.class);

    /**
     * Checks if a service is listening on a port on host.
     */
    public static boolean checkConnectivity(String host, int port, int timeoutMs) {
        return checkConnectivity(new InetSocketAddress(host, port), timeoutMs);
    }

    /**
     * Checks if a service is listening on a port on host.
     */
    public static boolean checkConnectivity(InetSocketAddress address, int timeoutMs) {
        Time time = new SystemTime();
        log.debug("Checking connectivity for " + address);

        long begin = time.milliseconds();
        long remainingWaitMs = timeoutMs;
        while (remainingWaitMs > 0) {
            // This is required to wait even if the service has not booted up yet.
            // The socket API may throw ConnectionRefusedException in some cases or
            // DNS resolution errors if the VM/container is booting up.
            Socket socket = null;
            try {
                socket = new Socket();
                socket.connect(address, timeoutMs);
                return true;
            } catch (IOException e) {
                //ConnectException is expected. Don't pollute the log.
                if (!(e instanceof java.net.ConnectException)) {
                    log.error(e.getMessage(), e);
                }
                // If you get an exception, wait for some time instead of busy polling.
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException ex) {
                    // Swallow exception because we want to retry until timeoutMs expires.
                }
            } finally {
                try {
                    if (socket != null) socket.close();
                } catch (IOException e) {
                    log.error(e.getMessage(), e);
                }
            }

            long elapsed = time.milliseconds() - begin;
            remainingWaitMs = timeoutMs - elapsed;
        }
        return false;
    }


    /**
     * Checks if the zookeeper cluster is ready to accept requests.
     *
     * @param zkConnectString Zookeeper connect string
     * @param timeoutMs       timeoutMs in milliseconds
     * @return true if the cluster is ready, false otherwise.
     */
    public static boolean isZookeeperReady(String zkConnectString, int timeoutMs) {

        ConnectStringParser connectStringParser = new ConnectStringParser(zkConnectString);

        // Wait for ZK process to start listening on the socket.
        boolean isAnyEndpointLive = false;
        for (InetSocketAddress node : connectStringParser.getServerAddresses()) {
            // If you find a live endpoint, exit the loop.
            if (checkConnectivity(node.getHostName(), node.getPort(), timeoutMs)) {
                isAnyEndpointLive = true;
                break;
            }
            log.error("Timed out waiting for endpoints: " + connectStringParser
                    .getServerAddresses());
        }

        if (isAnyEndpointLive) {

            ZooKeeper zookeeper = null;
            try {

                CountDownLatch waitForConnection = new CountDownLatch(1);

                boolean isSASLEnabled = false;
                if (System.getProperty("java.security.auth.login.config", null) != null) {
                    isSASLEnabled = true;
                }
                ZookeeperConnectionWatcher connectionWatcher =
                        new ZookeeperConnectionWatcher(waitForConnection, isSASLEnabled);
                zookeeper = new ZooKeeper(zkConnectString, timeoutMs, connectionWatcher);
                boolean timedOut = !waitForConnection.await(timeoutMs, TimeUnit.MILLISECONDS);

                if (timedOut) {
                    log.error("Timed out waiting for connection to " + zkConnectString);
                    return false;
                } else if (!connectionWatcher.isSuccessful()) {
                    log.error("Error occurred while connecting to zookeeper. " +
                            connectionWatcher.getFailureMessage());
                    return false;
                } else {
                    return true;
                }
            } catch (Exception e) {
                log.error(e.getMessage(), e);
                return false;
            } finally {
                if (zookeeper != null) {
                    try {
                        zookeeper.close();
                    } catch (InterruptedException e) {
                        log.error(e.getMessage(), e);
                    }
                }
            }
        }
        return false;
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

        KafkaMetadataClient adminClient = new KafkaMetadataClient(config);

        // Wait for Kafka process to start listening on the socket before making the metadata
        // request, otherwise the request fails.
        boolean isEndpointLive = false;
        for (InetSocketAddress brokerEndpoint : adminClient.getBrokerAddresses()) {
            // If you find a live endpoint, exit the loop.
            if (checkConnectivity(brokerEndpoint, timeoutMs)) {
                isEndpointLive = true;
                break;
            }
            log.error("Timed out waiting for endpoints: " + adminClient.getBrokerAddresses());
        }

        // If we have a live endpoint, get the metadata. If not return false.
        if (isEndpointLive) {

            Time time = new SystemTime();
            long begin = time.milliseconds();
            long remainingWaitMs = timeoutMs;
            List<Node> brokers = new ArrayList<>();
            while (remainingWaitMs > 0) {

                // The metadata query doesnot wait for all brokers to be ready before
                // returning the brokers. So, wait until expected brokers are present
                // or the time out expires.
                try {
                    brokers = adminClient.findAllBrokers(timeoutMs);
                    log.debug("Broker list: " + (brokers != null ? brokers : "[]"));
                    if ((brokers != null) && (brokers.size() >= minBrokerCount)) {
                        return true;
                    }
                } catch (Exception e) {
                    log.error(e.getMessage(), e);
                    // Swallow exceptions because we want to retry until timeoutMs expires.
                }

                try {
                    Thread.sleep(1000);
                } catch (InterruptedException ex) {
                    // Swallow exception because we want to retry until timeoutMs expires.
                }

                log.info("Trying again ...");
                long elapsed = time.milliseconds() - begin;
                remainingWaitMs = timeoutMs - elapsed;
            }

            if (brokers.size() < minBrokerCount)
                log.error(String.format("Expected %s brokers but found only %s. Brokers found %s",
                        minBrokerCount, brokers.size(), brokers));
        }

        return false;
    }

    /**
     * Gets metadata from Zookeeper. This method only waits for atleast one broker to be present.
     * @param zkConnectString Zookeeper connect string
     * @param timeoutMs Timeout in milliseconds
     * @return A list of broker metadata with atleast one broker.
     * @throws KeeperException
     * @throws InterruptedException
     * @throws IOException
     */
    private static List<String> getBrokerMetadataFromZookeeper(String zkConnectString, int
            timeoutMs) throws KeeperException, InterruptedException, IOException {
        ZooKeeper zookeeper = null;
        try {

            CountDownLatch waitForConnection = new CountDownLatch(1);

            boolean isSASLEnabled = false;
            if (System.getProperty("java.security.auth.login.config", null) != null) {
                isSASLEnabled = true;
            }
            ZookeeperConnectionWatcher connectionWatcher =
                    new ZookeeperConnectionWatcher(waitForConnection, isSASLEnabled);
            // Make it large enough that it will not expire for any of the preceding operations.
            int zkTimeoutMs = timeoutMs * 10;
            zookeeper = new ZooKeeper(zkConnectString, zkTimeoutMs, connectionWatcher);
            boolean timedOut = !waitForConnection.await(timeoutMs, TimeUnit.MILLISECONDS);

            if (timedOut) {
                String message = "Timed out waiting for connection to Zookeeper. timeout (ms) = " +
                        timeoutMs + ", Zookeeper connect = " + zkConnectString;
                throw new TimeoutException(message);
            } else if (!connectionWatcher.isSuccessful()) {
                throw new TimeoutException("Error occurred while connecting to zookeeper. " +
                        connectionWatcher.getFailureMessage());
            }

            // Make sure /brokers/ids exists. Countdown when node created event is triggered.
            CountDownLatch kafkaRegistrationSignal = new CountDownLatch(1);
            zookeeper.exists("/brokers/ids",
                    (event) -> {
                        System.out.println("exists : " + event.getType());
                        System.out.println("exists : " + event.getPath());
                        if (event.getType() == Watcher.Event.EventType.NodeCreated) {
                            kafkaRegistrationSignal.countDown();
                        }
                    },
                    (rc, path, ctx, stat) -> {
                        System.out.println("exists " + stat);
                        if (stat != null) {
                            kafkaRegistrationSignal.countDown();
                        }
                    },
                    null

            );

            boolean kafkaRegistrationTimedOut = !kafkaRegistrationSignal.await(
                    timeoutMs,
                    TimeUnit.MILLISECONDS);
            if (kafkaRegistrationTimedOut) {
                String message = "Timed out waiting  for Kafka to create /brokers/ids in Zookeeper. timeout (ms) = " +
                        timeoutMs + ", Zookeeper connect = " + zkConnectString;
                throw new TimeoutException(message);
            }

            // Get the data.
            CountDownLatch waitForBroker = new CountDownLatch(1);

            // Get children async. If the callback gets the data, then countdown otherwise wait for NodeChildrenChanged event.
            final List<String> brokers = new CopyOnWriteArrayList<>();
            zookeeper.getChildren("/brokers/ids",
                    (event) -> {
                        System.out.println("getchildren : " + event.getType());
                        System.out.println("getchildren : " + event.getPath());
                        if (event.getType() == Watcher.Event.EventType.NodeChildrenChanged) {
                            waitForBroker.countDown();
                        }
                    },
                    (rc, path, ctx, children) -> {
                        System.out.println("getchildren " + children);
                        if (children != null && children.size() > 0) {
                            children.forEach((child) -> brokers.add(child));
                            waitForBroker.countDown();
                        }
                    },
                    null
            );


            boolean waitForBrokerTimedOut = !waitForBroker.await(timeoutMs, TimeUnit.MILLISECONDS);
            if (waitForBrokerTimedOut) {
                throw new TimeoutException("Timed out waiting for Kafka to register brokers in Zookeeper. timeout (ms) = " +
                        timeoutMs + ", Zookeeper connect = " + zkConnectString);
            }
            // Get children if the callback had no children and the NodeChildrenChanged event is fired.
            if (brokers.size() == 0) {
                zookeeper.getChildren("/brokers/ids", false, null).forEach((child) -> brokers.add(child));
            }

            List<String> brokerMetadata = new ArrayList<>();

            for (String broker : brokers) {
                brokerMetadata.add(new String(zookeeper.getData("/brokers/ids/" + broker, false, null)));
            }
            return brokerMetadata;

        } finally {
            if (zookeeper != null) {
                try {
                    zookeeper.close();
                } catch (InterruptedException e) {
                    log.error(e.getMessage(), e);
                }
            }
        }
    }

    /**
     * Gets a kafka endpoint from Zookeeper. This method is used to get a broker for the bootstrap broker list.
     * This method is expected to used in conjunction with isKafkaReady to determine if Kafka is ready.
     * @param zkConnectString Zookeeper connect string
     * @param timeoutMs Timeout in milliseconds
     * @return A map of security-protocol->endpoints
     * @throws InterruptedException
     * @throws IOException
     * @throws KeeperException
     */
    public static Map<String, String> getKafkaEndpointFromZookeeper(
            String zkConnectString,
            int timeoutMs) throws InterruptedException, IOException, KeeperException {

        List<String> brokerMetadata = getBrokerMetadataFromZookeeper(zkConnectString, timeoutMs);

        String broker = brokerMetadata.get(0);

        System.out.println(broker);
        Map<String, String> endpointMap = new HashMap<>();
        Gson gson = new Gson();
        Type type = new TypeToken<Map<String, Object>>() {
        }.getType();
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
