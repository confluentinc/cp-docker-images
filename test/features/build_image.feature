Feature: build CP base docker containers

  Scenario: build a base image
    When I build image confluentinc/base from debian/base
    Then a confluentinc/base image should exist

  Scenario: Verify base image has java 8 installed
    Given image confluentinc/base exists
    When I run java -version on confluentinc/base
    Then output should have java version "1.8.0_91"

  Scenario: Verify base image has dub installed
    Given image confluentinc/base exists
    Then path /usr/local/bin/dub should exist in image confluentinc/base

  Scenario: Build a Zookeeper image
    Given image confluentinc/base exists
    When I build image confluentinc/zookeeper from debian/zookeeper
    Then a confluentinc/zookeeper image should exist


  Scenario: Verify Zookeeper image has confluent kafka installed
    Given image confluentinc/zookeeper exists
    Then path /etc/kafka should exist in image confluentinc/zookeeper
    Then path /etc/confluent should exist in image confluentinc/zookeeper


  Scenario Outline: Verify base image can execute zookeeper commands successfully
    Given image confluentinc/zookeeper exists
    When I run <command> on confluentinc/zookeeper
    Then output should have <snippet>

    Examples: Zookeeper commands
     | command         | snippet |
     | kafka-topics    | Create, delete, describe, or change a topic. |
     | zookeeper-server-start    | USAGE: /usr/bin/zookeeper-server-start [-daemon] zookeeper.properties |
     | zookeeper-server-stop     | No zookeeper server to stop |
