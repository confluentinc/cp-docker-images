# Pre-requisites

* Docker version 17.06.1-ce
* Docker Compose version 1.14.0 with Docker Compose file format 2.1
* [Confluent Cloud CLI](https://docs.confluent.io/current/cloud-quickstart.html#step-2-install-ccloud-cli)
* [An initialized Confluent Cloud cluster used for development only](https://confluent.cloud)

# Setup

Note: Use this in a *non-production* Confluent Cloud instance for development purposes only.

On the host from which you are running Docker, ensure that you have properly initialized Confluent CLI and have a valid configuration file at `$HOME/.ccloud/config`.

Step 1: Generate a file of ENV variables used by Docker Compose to set the bootstrap servers and security configuration

```bash
$ ./ccloud-generate-env-vars.sh
```

Step 2: Source that file of ENV variables

```bash
$ source ./delta_configs/env.delta
```

# Bring up services

You may bring up all services in the Docker Compose file at once or individually.

All services at once:

```bash
$ docker-compose up -d
```

## Confluent Schema Registry

```bash
$ docker-compose up -d schema-registry
```

## Kafka Connect

```bash
$ docker-compose up -d connect
```

## Confluent Control Center

```bash
$ docker-compose up -d connect
```

## KSQL Server

```bash
$ docker-compose up -d ksql-server
```

## KSQL CLI

```bash
$ docker-compose up -d ksql-cli
```

## Confluent REST Proxy

```bash
$ docker-compose up -d rest-proxy
```
