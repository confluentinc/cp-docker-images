Docker Images for Confluent Plaform
===

Docker images for deploying and running the Confluent Platform.  The images are currently available on [DockerHub](https://hub.docker.com/u/confluentinc/).  They are currently only available for Confluent Platform 3.0.1 and after.

Full documentation for using the images can be found [here](http://docs.confluent.io/current/cp-docker-images/docs/intro.html).

# Important Caveat - Images Not Tested for Docker for Mac or Windows
	
These images are not tested on Docker for Mac or Docker for Windows. These images will be updated in the near future to support these platforms. For more details on these known issues, you can refer to the following links:

* [Hostname Issue](https://forums.docker.com/t/docker-for-mac-does-not-add-docker-hostname-to-etc-hosts/8620/4)
* Host networking on Docker for Mac: [link 1](https://forums.docker.com/t/should-docker-run-net-host-work/14215), [link 2](https://forums.docker.com/t/net-host-does-not-work/17378/7), [link 3](https://forums.docker.com/t/explain-networking-known-limitations-explain-host/15205/4)

# Contribute

Start by reading our guidelines on contributing to this project found [here](http://docs.confluent.io/current/cp-docker-images/docs/contributing.html).

- Source Code: https://github.com/confluentinc/cp-docker-images
- Issue Tracker: https://github.com/confluentinc/cp-docker-images/issues


# License

The project is licensed under the Apache 2 license. For more information on the licenses for each of the individual Confluent Platform components packaged in the images, please refer to the respective [Confluent Platform documentation for each component](http://docs.confluent.io/current/platform.html).  

# Schema registry
1. Deployment
```
$ kubectl apply -f kubernetes/schema-registry/deployment.yml
```
Deploy schema registry container. This deployment uses secret that will be created in kafka connect stack. This deployment will be pending status until we deploy kafka connect.


2. Service
```
$ kubectl apply -f kubernetes/schema-registry/service.yml
```
Fixed IP address to make services talk each to each other transparently.


# Kafka Connect

1. Create secrets
```
apiVersion: v1
kind: Secret
metadata:
  name: kafka-connect-bootstrap
type: Opaque
data:
  db-pipelines-username: a2Fma2FfcmVhZGVy
  db-pipelines-password: REPLACE_ME
  connect-sasl-jaas-config: REPLACE_ME
  connect-producer-sasl-jaas-config: REPLACE_ME

```
Find values that must be replaced

```
$ echo -e "my#53cur3@p455" | base64
bXkjNTNjdXIzQHA0NTUK
```
Generate base64 to populate file. The output bXkjNTNjdXIzQHA0NTUK should go in db-pipelines-password.
Do the same for each value.

```
$ kubectl apply -f kubernetes/kafka-connect/secret.yml
```


2. Create config
```
$ kubectl apply -f kubernetes/kafka-connect/config.yml
```
This config will be used to bootstrap kafka-connect.


3. Batch job
```
$ kubectl apply -f kubernetes/kafka-connect/batch.yml
```
This container with type batch will run once to bootstrap kafka.


4. Deployment
```
$ kubectl apply -f kubernetes/kafka-connect/deployment.yml
```
This is the deployment itself (containers that runs application)


5. Service
```
$ kubectl apply -f kubernetes/kafka-connect/service.yml
```
This is the LB for talking to multiples containers.
