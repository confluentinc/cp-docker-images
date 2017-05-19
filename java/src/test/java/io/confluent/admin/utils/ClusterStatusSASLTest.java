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

import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.common.config.types.Password;
import org.apache.kafka.common.protocol.SecurityProtocol;
import org.apache.kafka.common.utils.Utils;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Map;
import java.util.Properties;

import static org.assertj.core.api.Assertions.assertThat;


public class ClusterStatusSASLTest {

  private static final Logger log = LoggerFactory.getLogger(ClusterStatusSASLTest.class);

  private static EmbeddedKafkaCluster kafka;


  @BeforeClass
  public static void setup() throws IOException {
    kafka = new EmbeddedKafkaCluster(3, 3, true);
    kafka.start();
  }


  @AfterClass
  public static void tearDown() {
    kafka.shutdown();
  }

  @Test(timeout = 120000)
  public void zookeeperReadyWithSASL() throws Exception {
    assertThat(ClusterStatus.isZookeeperReady(this.kafka.getZookeeperConnectString(), 10000))
        .isTrue();
  }

  @Test(timeout = 120000)
  public void isKafkaReadyWithSASLAndSSL() throws Exception {
    Properties clientSecurityProps = kafka.getClientSecurityConfig();

    Map<String, String> config = Utils.propsToStringMap(clientSecurityProps);
    config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapBroker
        (SecurityProtocol.SASL_SSL));

    // Set password and enabled protocol as the Utils.propsToStringMap just returns toString()
    // representations and these properties don't have a valid representation.
    Password trustStorePassword = (Password) clientSecurityProps.get("ssl.truststore.password");
    config.put("ssl.truststore.password", trustStorePassword.value());
    config.put("ssl.enabled.protocols", "TLSv1.2");

    assertThat(ClusterStatus.isKafkaReady(config, 3, 10000)).isTrue();
  }


  @Test(timeout = 120000)
  public void isKafkaReadyWithSASLAndSSLUsingZK() throws Exception {
    Properties clientSecurityProps = kafka.getClientSecurityConfig();

    boolean zkReady = ClusterStatus.isZookeeperReady(this.kafka.getZookeeperConnectString(), 30000);
    if (!zkReady) {
      throw new RuntimeException(
          "Could not reach zookeeper " + this.kafka.getZookeeperConnectString());
    }
    Map<String, String> endpoints = ClusterStatus.getKafkaEndpointFromZookeeper(
        this.kafka.getZookeeperConnectString(),
        30000
    );

    String bootstrap_broker = endpoints.get("SASL_SSL");
    Map<String, String> config = Utils.propsToStringMap(clientSecurityProps);
    config.put(CommonClientConfigs.BOOTSTRAP_SERVERS_CONFIG, bootstrap_broker);

    // Set password and enabled protocol as the Utils.propsToStringMap just returns toString()
    // representations and these properties don't have a valid representation.
    Password trustStorePassword = (Password) clientSecurityProps.get("ssl.truststore.password");
    config.put("ssl.truststore.password", trustStorePassword.value());
    config.put("ssl.enabled.protocols", "TLSv1.2");

    assertThat(ClusterStatus.isKafkaReady(config, 3, 10000)).isTrue();
  }


}
