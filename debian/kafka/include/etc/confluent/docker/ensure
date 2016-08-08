#!/usr/bin/env bash

set -o nounset \
    -o errexit \
    -o verbose \
    -o xtrace

export KAFKA_DATA_DIRS=${KAFKA_DATA_DIRS:-"/var/lib/kafka/data"}
echo "===> Check if $KAFKA_DATA_DIRS is writable ..."
dub path "$KAFKA_DATA_DIRS" writable

echo "===> Check if Zookeeper is healthy ..."
cub zk-ready "$KAFKA_ZOOKEEPER_CONNECT" "${KAFKA_CUB_ZK_TIMEOUT:-40}"
