Docker images for Confluent Plaform
===

Supported OS
--
1. Debian 8 (Jessie)


Versions
--
Confluent Platform : 3.0.0

Java : Azul Zulu JRE 


Overview
====

The bootup process
----

The entrypoint `/etc/confluent/docker/run` runs three executable in the `/etc/confluent/docker` in the following sequence:

`/etc/confluent/docker/configure`

`/etc/confluent/docker/ensure`

`/etc/confluent/docker/launch`

###Configuration

The `configure` script does all the configuration. This includes :

- Creating all configuration files and copying them to their proper location
- It is also responsible for handling service discovery if required.

###Preflight checks
The `ensure` scripts makes sure that all the prerequisites for launching the service are in place. This includes:

- Ensure the configuration files are present and readable.
- Ensure that you can write/read to the data directory. The directories need to be world writable.
- Ensuring supporting services are in READY state. For example, ensure that ZK is ready before launching Kafka broker.
- Ensure supporting systems are configured properly. For example, make sure all topics required for C3 are created with proper replication, security and partition settings.

###Launching the process

The `launch` script runs the actual process. The script should ensure that :

- The process is run properly. You need to do `exec` (Note to self: Why was this needed again?)
- Log to stdout

Guidelines for the scripts
----
- Make it executable
- Fail fast
- Fail with good error messages
- Return 0 if success, 1 if fail



How to extend the images ?
----
You can extend the images to fit your build/deploy system.

How to :

1. Add more software ? (For eg : New relic monitoring)
2. Use the server.properties that puppet/chef generated ?
3. How to use service discovery ?
4. How to add my own preflight checks ?
5. How to log to files instead of stdout ?

Utility scripts
----

### Docker Utility Belt (dub)

1. Template

		usage: dub template [-h] input output

		Generate template from env vars.

		positional arguments:
		  input       Path to template file.
		  output      Path of output file.

2. ensure

		usage: dub ensure [-h] name

		Check if env var exists.

		positional arguments:
		  name        Name of env var.

3. wait

		usage: dub wait [-h] host port timeout

		wait for network service to appear.

		positional arguments:
		  host        Host.
		  port        Host.
		  timeout     timeout in secs.
4. path

		usage: dub path [-h] path {writable,readable,executable,exists}

		Check for path permissions and existence.

		positional arguments:
		  path                  Full path.
		  {writable,readable,executable,exists} One of [writable, readable, executable, exists].


### Confluent Platform Utility Belt (cub)

1. zk-ready

		usage: cub zk-ready [-h] connect_string timeout retries wait

		Check if ZK is ready.

		positional arguments:
		  connect_string  Zookeeper connect string.
		  timeout         Time in secs to wait for service to be ready.
		  retries         No of retries to check if leader election is complete.
		  wait            Time in secs between retries
2. kafka-ready

		usage: cub kafka-ready [-h] connect_string min_brokers timeout retries wait

		Check if Kafka is ready.

		positional arguments:
		  connect_string  Zookeeper connect string.
		  min_brokers     Minimum number of brokers to wait for
		  timeout         Time in secs to wait for service to be ready.
		  retries         No of retries to check if leader election is complete.
		  wait            Time in secs between retries


Development
==

###Setup

1. Install docker

		brew install docker docker-machine

2. Create a docker machine.

		docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent
	This command local env but it is recommended that you create one on AWS. The builds are much faster and is more predictable (virtualbox stops when you close the lid of the laptop and sometimes gets into a weird state).

	[Docker Machine AWS Example](https://docs.docker.com/machine/examples/aws/)

	`m4.large` is good choice : It has 2 vCPUs with 8GB RAM and costs around ~$88 monthly.

		export INSTANCE_NAME=$USER-docker-machine
		docker-machine create \
			--driver amazonec2 \
			--amazonec2-region us-west-2 \
			--amazonec2-instance-type m4.large \
			--amazonec2-root-size 100 \
			--amazonec2-ami ami-16b1a077 \
			--amazonec2-tags Name,$INSTANCE_NAME \
			aws-confluent
3. Setup env

		eval $(docker-machine env confluent)


###Building the images

```make build-debian```

You can run build tests by running `make test-build`. Use this when you want to test the builds with a clean slate. This deletes all images and starts from scratch.

###Running tests

You'll need to first install virtualenv: `pip install virtualenv`

	cd cp-docker-images
	make test-zookeeper
	make test-kafka

Running a single test: `venv/bin/py.test tests/test_zookeeper.py::ConfigTest -v`

###Delete all docker containers

```docker rm -f $(docker ps -a -q)```


References
---
###Docker best practices

https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

https://github.com/lwieske/dockerfiles-java-8/blob/master/Dockerfile.slim

https://docs.openshift.com/enterprise/3.0/creating_images/guidelines.html#general-docker-guidelines

###Bridged vs host-only
https://github.com/docker/docker/issues/7857
