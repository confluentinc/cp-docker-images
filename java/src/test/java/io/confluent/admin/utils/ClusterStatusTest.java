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
import org.apache.kafka.common.utils.SystemTime;
import org.apache.kafka.common.utils.Time;
import org.assertj.core.data.Offset;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.fail;

public class ClusterStatusTest {

    private static EmbeddedKafkaCluster kafka;
    private static int numBrokers = 3;
    private static int numZookeeperPeers = 3;

    @BeforeClass
    public static void setup() throws IOException {

        kafka = new EmbeddedKafkaCluster(numBrokers, numZookeeperPeers);
        kafka.start();
    }

    @AfterClass
    public static void tearDown() {
        kafka.shutdown();
    }

    @Test(timeout = 120000)
    public void zookeeperReady() throws Exception {
        assertThat(
                ClusterStatus.isZookeeperReady(this.kafka.getZookeeperConnectString(), 10000))
                .isTrue();
    }

    @Test(timeout = 120000)
    public void isKafkaReady() throws Exception {

        Map<String, String> config = new HashMap<>();
        config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapBroker
                (SecurityProtocol.PLAINTEXT));
        assertThat(ClusterStatus.isKafkaReady(config, 3, 10000))
                .isTrue();
    }

    @Test(timeout = 120000)
    public void isKafkaReadyFailWithLessBrokers() throws Exception {
        try {
            Map<String, String> config = new HashMap<>();
            config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapBroker
                    (SecurityProtocol.PLAINTEXT));
            assertThat(ClusterStatus.isKafkaReady(config, 5, 10000))
                    .isFalse();
        } catch (Exception e) {
            fail("Unexpected error. " + e.getMessage());
        }

    }

    @Test(timeout = 120000)
    public void isKafkaReadyWaitFailureWithNoBroker() throws Exception {
        try {
            Map<String, String> config = new HashMap<>();
            config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, "localhost:6789");
            assertThat(ClusterStatus.isKafkaReady(config, 3, 10000)).isFalse();
        } catch (Exception e) {
            fail("Unexpected error." + e.getMessage());
        }
    }

    @Test(timeout = 120000)
    public void checkConnectivity() throws Exception {
        String broker = this.kafka.getBootstrapBroker(SecurityProtocol.PLAINTEXT);
        int port = Integer.parseInt(broker.split(":")[1]);
        assertThat(ClusterStatus.checkConnectivity("localhost", port, 3000)).isTrue();
    }

    @Test(timeout = 120000)
    public void checkConnectivityFailure() throws Exception {
        Time time = new SystemTime();
        long start = time.milliseconds();
        assertThat(ClusterStatus.checkConnectivity("localhost", 12345, 3000)).isFalse();
        assertThat(time.milliseconds() - start).isCloseTo(3000L, Offset.offset(500L));
    }


}
