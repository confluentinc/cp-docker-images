# Pre-requisites

* Docker version 17.06.1-ce
* Docker Compose version 1.14.0 with Docker Compose file format 2.1
* [Confluent Cloud CLI](https://docs.confluent.io/current/cloud-quickstart.html#step-2-install-ccloud-cli)
* [An initialized Confluent Cloud cluster used for development only](https://confluent.cloud)

# Instructions

Use this in a non-production Confluent Cloud instance. Ensure that you have properly initialized Confluent CLI on this host and have a valid configuration file at `$HOME/.ccloud/config`

Steps:

```bash
$ ./ccloud-generate-cp-configs.sh
$ source ./delta_configs/env.delta
$ docker-compose up -d
```
