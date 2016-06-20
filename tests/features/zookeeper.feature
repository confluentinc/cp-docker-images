Feature: Verify CP Zookeeper docker container

  Scenario: build a base image
    When I build image confluentinc/base from debian/base
    Then a confluentinc/base image should exist

  Scenario: Verify base image has java 8 installed
    Given image confluentinc/base exists
    When I run java -version on confluentinc/base
    Then output should have java version "1.8.0_91"
