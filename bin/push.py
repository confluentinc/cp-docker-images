#!/usr/bin/env python3
from subprocess import Popen, call, check_call

foo = [
"base",
"enterprise-kafka",
"enterprise-replicator-executable",
"kafkacat",
"kafka-connect-base",
"kafka-rest",
"zookeeper",
"enterprise-control-center",
"enterprise-replicator",
"kafka",
"kafka-connect",
"kafka-mqtt",
"schema-registry"
]

docker_repo_url = "368821881613.dkr.ecr.us-west-2.amazonaws.com"
#docker_repo_url = "confluent-docker.jfrog.io"

passw = "AKCp5btKzpjCQgCGHZvfEiNFZFYNzUZZr39t69UaEgQX9SEcyACoTrECnxK6cL9Li74ZQ9sw4"
usern = "platform-ops-jfrog@confluent.io"

version = "5.3.0-SNAPSHOT"

images_to_push = [f"confluentinc/cp-rpm-{ff}" for ff in foo]

for redhat_image_name in images_to_push:
    check_call(f"docker tag {redhat_image_name}:{version} {docker_repo_url}/{redhat_image_name}:{version}", shell=True)
    check_call(f"docker push {docker_repo_url}/{redhat_image_name}:{version}", shell=True)
    #check_call(f"echo docker pull {docker_repo_url}/{redhat_image_name}:{version}", shell=True)
