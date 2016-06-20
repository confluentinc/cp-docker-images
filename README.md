Docker images for Confluent Plaform
===

Supported OS
--
1. Ubuntu 15.10
2. Alpine Linux 3.4

Versions
--
Confluent Platform : 3.0.0

Java : Oracle JRE 


Overview
==

The bootup process
--

The entrypoint `/etc/confluent/docker/run` runs three executable in the `/etc/confluent/docker` in the following sequence:

`/etc/confluent/docker/configure`

`/etc/confluent/docker/ensure`

`/etc/confluent/docker/launch`

Configuration
--

The `configure` script does all the configuration. This includes :

- Creating all configuration files and copying them to their proper location
- It is also responsible for handling service discovery if required.

Preflight checks
--

The `ensure` scripts makes sure that all the prerequisites for launching the service are in place. This includes:

- Ensure the configuration files are present and readable.
- Ensure that you can write/read to the data directory. The directories need to be world writable.
- Ensuring supporting services are in READY state. For example, ensure that ZK is ready before launching Kafka broker.
- Ensure supporting systems are configured properly. For example, make sure all topics required for C3 are created with proper replication, security and partition settings.

Launching the process
--
The `launch` script runs the actual process. The script should ensure that :

- The process is run properly. You need to do `exec` (Note to self: Why was this needed again?)
- Log to stdout

Guidelines for the scripts
---
- Make it executable
- Fail fast 
- Fail with good error messages
- Return 0 if success, 1 if fail



How to extend the images ?
--
You can extend the images to fit your build/deploy system. 

How to : 

1. Add more software ? (For eg : New relic monitoring)
2. Use the server.properties that puppet/chef generated ?
3. How to use service discovery ?
4. How to add my own preflight checks ?
5. How to log to files instead of stdout ?


Development
==

Setup
---
1. Install docker 

		brew install docker docker-machine
		
2. Create a docker machine.

		docker-machine create --driver virtualbox confluent
		
3. Setup env

		eval $(docker-machine env confluent)
		

Building the images
---

`make build-debian`

Running tests
---

`make test`


Docker best practices
---

https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/
https://github.com/lwieske/dockerfiles-java-8/blob/master/Dockerfile.slim
https://docs.openshift.com/enterprise/3.0/creating_images/guidelines.html#general-docker-guidelines
