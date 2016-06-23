Feature: Verify CP Zookeeper docker container

  Scenario: Verify error when required properties are missing
    Given an image confluentinc/zookeeper exists
    When I start confluentinc/zookeeper
    Then I should see SERVER_ID is required
    And shutdown cleanly

  Scenario: Verify configuration is generated with defaults
    Given image confluentinc/zookeeper exists
    And the environment variables are
       | name          | value  |
       | SERVER_ID     | 1   |

    When I start confluentinc/zookeeper
    Then it should have /etc/kafka/zookeeper.properties with default properties
    And shutdown cleanly

  Scenario: Verify configuration is generated with env
    Given image confluentinc/zookeeper exists
    And the environment variables are
       | name          | value  |
       | SERVER_ID     | 1   |

    When I start confluentinc/zookeeper
    Then it should have /etc/kafka/zookeeper.properties with env properties
    And shutdown cleanly


  Scenario: Verify configuration is generated with defaults
    Given the environment variables are
       | name          | value  |
       | SERVER_ID     | 1   |

    And volumes mapping

    When I start a zookeeper cluster with 1 node
    Then it should have /etc/kafka/zookeeper.properties with default properties
    And shutdown cleanly
