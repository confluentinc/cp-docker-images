Feature: build CP base docker containers

  Scenario: build a base image
    When I build confluentinc/base from debian/base
    Then a confluentinc/base image should exist

  Scenario: Check if base image has java 8 installed
    Given image confluentinc/base exists
    When I run java -version on confluentinc/base
    Then output should have java version "1.8.0_91"

  Scenario: Check if base image has dub installed
    Given image confluentinc/base exists
    Then path /usr/local/bin/dub should exist in image confluentinc/base

  Scenario: build a zk image
    Given image confluentinc/base exists
    When I build confluentinc/zk from debian/zk
    Then a confluentinc/zk image should exist
