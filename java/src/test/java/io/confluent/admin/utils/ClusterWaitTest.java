/**
 * Copyright 2016 Confluent Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package io.confluent.admin.utils;

import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.common.protocol.SecurityProtocol;
import org.junit.Test;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.fail;

public class ClusterWaitTest {

    @Test(timeout = 180000)
    public void isZookeeperReadyWait() throws IOException, InterruptedException {
        final EmbeddedZookeeperEnsemble zookeeperWait = new EmbeddedZookeeperEnsemble(3, 22222);
        Thread zkClusterThread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Thread.sleep(20000);
                    zookeeperWait.start();
                    while (zookeeperWait.isRunning()) {
                        Thread.sleep(1000);
                    }
                } catch (Exception e) {
                    // Just fail.
                    fail("Unexpected error." + e.getMessage());
                }
            }
        });

        zkClusterThread.start();

        try {
            assertThat(ClusterStatus.isZookeeperReady(zookeeperWait.connectString(), 30000))
                    .isTrue();

        } catch (Exception e) {
            fail("Unexpected error." + e.getMessage());
        } finally {
            zookeeperWait.shutdown();
        }
        zkClusterThread.join(60000);
    }

    @Test(timeout = 180000)
    public void isKafkaReadyWait() throws Exception {
        final EmbeddedKafkaCluster kafkaWait = new EmbeddedKafkaCluster(3, 3);

        Thread kafkaClusterThread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Thread.sleep(1000);
                    kafkaWait.start();
                    while (kafkaWait.isRunning()) {
                        Thread.sleep(1000);
                    }
                } catch (Exception e) {
                    fail("Unexpected exception ", e);
                }
            }
        });

        kafkaClusterThread.start();

        try {
            Map<String, String> config = new HashMap<>();
            config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, kafkaWait.getBootstrapBroker
                    (SecurityProtocol.PLAINTEXT));


            assertThat(ClusterStatus.isKafkaReady(config, 3, 10000))
                    .isTrue();
        } catch (Exception e) {
            fail("Unexpected error." + e.getMessage());
        } finally {
            kafkaWait.shutdown();
        }
        kafkaClusterThread.join(60000);
    }


    @Test(timeout = 180000)
    public void isKafkaReadyWaitUsingZooKeeper() throws Exception {
        final EmbeddedKafkaCluster kafkaWait = new EmbeddedKafkaCluster(3, 3);

        Thread kafkaClusterThread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Thread.sleep(1000);
                    kafkaWait.start();
                    while (kafkaWait.isRunning()) {
                        Thread.sleep(1000);
                    }
                } catch (Exception e) {
                    fail("Unexpected exception ", e);
                }
            }
        });

        kafkaClusterThread.start();
        try {

            boolean zkReady = ClusterStatus.isZookeeperReady(kafkaWait.getZookeeperConnectString(), 30000);

            if (! zkReady) {
                fail("Could not reach zookeeper " + kafkaWait.getZookeeperConnectString());
            }

            Map<String, String> endpoints = ClusterStatus.getKafkaEndpointFromZookeeper(
                    kafkaWait.getZookeeperConnectString(),
                    30000);

            String bootstrap_broker = endpoints.get("PLAINTEXT");
            Map<String, String> config = new HashMap<>();
            config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, bootstrap_broker);


            assertThat(ClusterStatus.isKafkaReady(config, 3, 10000))
                    .isTrue();
        } catch (Exception e) {
            fail("Unexpected error." + e.getMessage());
        } finally {
            kafkaWait.shutdown();
        }
        kafkaClusterThread.join(60000);
    }
}
