Feature: build CP base docker containers

  Scenario: build a base image
    When I build image confluentinc/base from debian/base
    Then a confluentinc/base image should exist

  Scenario: Verify base image has java 8 installed
    Given an image confluentinc/base exists
    When I run java -version on it
    Then I should see java version "1.8.0_91"

  Scenario: Verify base image has dub installed
    Given an image confluentinc/base exists
    Then it should have path /usr/local/bin/dub

  Scenario: Build a Zookeeper image
    Given an image confluentinc/base exists
    When I build image confluentinc/zookeeper from debian/zookeeper
    Then a confluentinc/zookeeper image should exist


  Scenario: Verify Zookeeper image has confluent kafka installed
    Given an image confluentinc/zookeeper exists
    Then it should have path /etc/kafka
    Then it should have path /etc/confluent

  Scenario Outline: Verify confluent/zookeeper has bootup scripts
    Given an image confluentinc/zookeeper exists
    Then it should have executable <path>

    Examples: Bootup scripts
     | path         |
     | /etc/confluent/docker/configure    |
     | /etc/confluent/docker/ensure       |
     | /etc/confluent/docker/launch       |


  Scenario Outline: Verify confluent/zookeeper image can execute zookeeper commands successfully
    Given an image confluentinc/zookeeper exists
    When I run <command> on it
    Then I should see <snippet>

    Examples: Zookeeper commands
     | command                   | snippet |
     | kafka-topics              | Create, delete, describe, or change a topic. |
     | zookeeper-server-start    | USAGE: /usr/bin/zookeeper-server-start [-daemon] zookeeper.properties |
     | zookeeper-server-stop     | No zookeeper server to stop |
