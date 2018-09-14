# Pre-requisites

* Docker version 17.06.1-ce
* Docker Compose version 1.14.0 with Docker Compose file format 2.1
* [Confluent Cloud CLI](https://docs.confluent.io/current/cloud-quickstart.html#step-2-install-ccloud-cli)
* [An initialized Confluent Cloud cluster used for development only](https://confluent.cloud)

# Instructions

Use this in a non-production Confluent Cloud instance. Ensure that you have properly initialized Confluent CLI on this host and have a valid configuration file at `$HOME/.ccloud/config`

Step 1: Generate a file of ENV variables used by Docker Compose to set the bootstrap servers and security configuration

```bash
$ ./ccloud-generate-env-vars.sh
```

Step 2: Source that file of ENV variables

```bash
$ source ./delta_configs/env.delta
```

Step 3: Bring up the Docker environment with Docker Compose

```bash
$ docker-compose up -d
```
