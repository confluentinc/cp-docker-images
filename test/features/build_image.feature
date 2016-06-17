Feature: build CP base docker containers

  Scenario: build a base image
    When I build confluentinc/base from debian/base
    Then a confluentinc/base image should exist
