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

import org.apache.zookeeper.WatchedEvent;
import org.apache.zookeeper.Watcher;

import java.util.concurrent.CountDownLatch;

/**
 * Waits for SyncConnected. When SASL is enabled, waits for both SyncConnected and
 * SaslAuthenticated events.
 * <p>
 * In case of an AuthFailed event, isSuccessful is set to false. This should be verified in the
 * code using this class and failure message should be logged.
 */
public class ZookeeperConnectionWatcher implements Watcher {

  private CountDownLatch connectSignal;
  private boolean isSuccessful = true;
  private String failureMessage = null;
  private boolean isSASLEnabled = false;

  public ZookeeperConnectionWatcher(CountDownLatch connectSignal, boolean isSASLEnabled) {
    this.connectSignal = connectSignal;
    this.isSASLEnabled = isSASLEnabled;
  }

  public boolean isSuccessful() {
    return isSuccessful;
  }

  public String getFailureMessage() {
    return failureMessage;
  }

  @Override
  public void process(WatchedEvent event) {
    if (event.getType() == Event.EventType.None) {
      switch (event.getState()) {
        case SyncConnected:
          // If SASL is enabled, we want to wait for the SaslAuthenticated event.
          if (!isSASLEnabled) {
            connectSignal.countDown();
          }
          break;
        case Expired:
          failureMessage = "Session expired.";
          isSuccessful = false;
          connectSignal.countDown();
          break;
        case Disconnected:
          failureMessage = "Disconnected from the server.";
          isSuccessful = false;
          connectSignal.countDown();
          break;
        case AuthFailed:
          failureMessage = "Authentication failed.";
          isSuccessful = false;
          connectSignal.countDown();
          break;
        case SaslAuthenticated:
          connectSignal.countDown();
          break;
      }
    }
  }
}
