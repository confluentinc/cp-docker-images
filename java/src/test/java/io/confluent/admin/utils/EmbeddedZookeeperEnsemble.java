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

import org.apache.zookeeper.client.FourLetterWordMain;
import org.apache.zookeeper.server.quorum.Election;
import org.apache.zookeeper.server.quorum.QuorumPeer;
import org.apache.zookeeper.test.ClientBase;
import org.apache.zookeeper.test.JMXEnv;
import org.junit.Assert;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeoutException;

/**
 * This class is based on code from Apache Zookeeper unit tests listed below.
 *
 * src/java/test/org/apache/zookeeper/test/ClientBase.java
 * src/java/test/org/apache/zookeeper/test/SaslClientTest.java
 * src/java/test/org/apache/zookeeper/test/SaslAuthTest.java
 */
public class EmbeddedZookeeperEnsemble {

    private static final Logger log = LoggerFactory.getLogger(EmbeddedZookeeperEnsemble.class);
    private static int CONNECTION_TIMEOUT = 30000;
    private static String LOCAL_ADDR = "localhost";
    private final Map<Integer, QuorumPeer> quorumPeersById = new ConcurrentHashMap<>();
    private int basePort = 11111;
    private String hostPort = "";
    private int tickTime = 2000;
    private int initLimit = 3;
    private int syncLimit = 3;
    private boolean isRunning = false;

    private int numNodes;

    public EmbeddedZookeeperEnsemble(int numNodes) throws IOException {
        this(numNodes, 11111);
    }

    public EmbeddedZookeeperEnsemble(int numNodes, int basePort) throws IOException {
        this.numNodes = numNodes;
        this.basePort = basePort;
        initialize();
    }

    private void initialize() throws IOException {
        HashMap peers = new HashMap();
        for (int i = 0; i < numNodes; i++) {

            int port = basePort++;
            int portLE = basePort++;


            peers.put(Long.valueOf(i), new QuorumPeer.QuorumServer(Long.valueOf(i),
                    new InetSocketAddress(LOCAL_ADDR, port + 1000),
                    new InetSocketAddress(LOCAL_ADDR, portLE + 1000),
                    QuorumPeer.LearnerType.PARTICIPANT));
        }


        for (int i = 0; i < numNodes; i++) {

            File dir = Files.createTempDirectory("zk" + i).toFile();

            int portClient = basePort++;
            log.info("creating QuorumPeer " + i + " port " + portClient);
            QuorumPeer s = new QuorumPeer(peers, dir, dir, portClient, 3, i, tickTime, initLimit,
                    syncLimit);
            Assert.assertEquals(portClient, s.getClientPort());

            quorumPeersById.put(i, s);

            if (i == 0) {
                hostPort = LOCAL_ADDR + ":" + portClient;
            } else {
                hostPort = hostPort + "," + LOCAL_ADDR + ":" + portClient;
            }

        }
    }

    public String connectString() {
        return hostPort;
    }

    public void start() throws IOException {


        JMXEnv.setUp();

        for (int i = 0; i < numNodes; i++) {
            log.info("start QuorumPeer " + i);
            QuorumPeer s = quorumPeersById.get(i);
            s.start();
        }

        log.info("Checking ports " + hostPort);

        for (String hp : hostPort.split(",")) {
            Assert.assertTrue("waiting for server up",
                    ClientBase.waitForServerUp(hp,
                            CONNECTION_TIMEOUT));
            log.info(hp + " is accepting client connections");
            try {
                log.info(send4LW(hp, CONNECTION_TIMEOUT, "stat"));
            } catch (TimeoutException e) {
                log.error(e.getMessage(), e);
            }

        }

        JMXEnv.dump();
        isRunning = true;
    }

    public String send4LW(String hp, long timeout, String FourLW) throws TimeoutException {
        long start = System.currentTimeMillis();

        while (true) {
            try {
                HostPort e = (HostPort) parseHostPortList(hp).get(0);
                String result = FourLetterWordMain.send4LetterWord(e.host, e.port, FourLW);
                return result;
            } catch (IOException var7) {
                log.info("server " + hp + " not up " + var7);
            }

            if (System.currentTimeMillis() > start + timeout) {
                throw new TimeoutException();
            }

            try {
                Thread.sleep(250L);
            } catch (InterruptedException e) {
                //Ignore
            }
        }
    }

    private List<HostPort> parseHostPortList(String hplist) {
        ArrayList<HostPort> alist = new ArrayList<HostPort>();
        for (String hp : hplist.split(",")) {
            int idx = hp.lastIndexOf(':');
            String host = hp.substring(0, idx);
            int port;
            try {
                port = Integer.parseInt(hp.substring(idx + 1));
            } catch (RuntimeException e) {
                throw new RuntimeException("Problem parsing " + hp + e.toString());
            }
            alist.add(new HostPort(host, port));
        }
        return alist;
    }

    public void shutdown() {
        for (int i = 0; i < quorumPeersById.size(); i++) {
            shutdown(quorumPeersById.get(i));
        }

        String[] hostPorts = this.hostPort.split(",");
        int numServers = hostPorts.length;

        for (int i = 0; i < numServers; ++i) {
            String hp = hostPorts[i];
            Assert.assertTrue("waiting for server down", ClientBase.waitForServerDown(hp, (long)
                    ClientBase.CONNECTION_TIMEOUT));
            log.info(hp + " is no longer accepting client connections");
        }

        JMXEnv.tearDown();
        isRunning = false;
    }

    private void shutdown(QuorumPeer qp) {
        try {
            log.info("Shutting down quorum peer " + qp.getName());
            qp.shutdown();
            Election e = qp.getElectionAlg();
            if (e != null) {
                log.info("Shutting down leader election " + qp.getName());
                e.shutdown();
            } else {
                log.info("No election available to shutdown " + qp.getName());
            }

            log.info("Waiting for " + qp.getName() + " to exit thread");
            qp.join(30000L);
            if (qp.isAlive()) {
                Assert.fail("QP failed to shutdown in 30 seconds: " + qp.getName());
            }
        } catch (InterruptedException var2) {
            log.debug("QP interrupted: " + qp.getName(), var2);
        }

    }

    public boolean isRunning() {
        return isRunning;
    }


    public static class HostPort {
        String host;
        int port;

        public HostPort(String host, int port) {
            this.host = host;
            this.port = port;
        }
    }

}
