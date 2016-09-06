package io.confluent.admin.utils;

import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.common.protocol.SecurityProtocol;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.fail;

public class KafkaAdminClientTest {

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
    public void testFindAllBrokers() throws Exception {

        try {
            Map<String, String> config = new HashMap<>();
            config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapBroker(SecurityProtocol.PLAINTEXT));
            assertThat(new KafkaAdminClient(config).findAllBrokers(10000).size()).isEqualTo(3);
        } catch (Exception e) {
            fail("Unexpected error." + e.getMessage());
        }
    }

    @Test(timeout = 120000)
    public void testFindAllBrokersFail() throws Exception {

        try {
            Map<String, String> config = new HashMap<>();
            config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, "localhost:12345");
            assertThat(new KafkaAdminClient(config).findAllBrokers(10000)).isNull();
        } catch (Exception e) {
            fail("Unexpected error." + e.getMessage());
        }
    }
}