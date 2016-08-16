Development
===========


Setup
~~~~~

1. Install docker

   ::

       brew install docker docker-machine

2. Create a docker machine.

   ::

       docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent

   This command local env but it is recommended that you create one on
   AWS. The builds are much faster and more predictable (virtualbox
   stops when you close the lid of the laptop and sometimes gets into a
   weird state).

   `Docker Machine AWS
   Example <https://docs.docker.com/machine/examples/aws/>`__

   ``m4.large`` is good choice : It has 2 vCPUs with 8GB RAM and costs
   around ~$88 monthly.

   ::

       export INSTANCE_NAME=$USER-docker-machine
       docker-machine create \
           --driver amazonec2 \
           --amazonec2-region us-west-2 \
           --amazonec2-instance-type m4.large \
           --amazonec2-root-size 100 \
           --amazonec2-ami ami-16b1a077 \
           --amazonec2-tags Name,$INSTANCE_NAME \
           $USER-aws-confluent

3. Setup env

   ::

       eval $(docker-machine env confluent)

Building the images
~~~~~~~~~~~~~~~~~~~

   ::

      make build-debian

You can run build tests by running ``make test-build`` . Use this when
you want to test the builds with a clean slate. This deletes all images
and starts from scratch.

Running tests
~~~~~~~~~~~~~

You'll need to first install virtualenv: ``pip install virtualenv``

::

    cd cp-docker-images
    make test-zookeeper
    make test-kafka

Running a single test:
``venv/bin/py.test tests/test_zookeeper.py::ConfigTest -v``

Delete all docker containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``docker rm -f $(docker ps -a -q)``


Make targets
------------
`clean-images` will delete all images tagged with `label=io.confluent.docker.testing=true`

`clean-containers` will delete all containers tagged with `label=io.confluent.docker`

`tag-remote` will tag images for the repository in DOCKER_REMOTE_REPOSITORY.

`push-private` will push images to the private repository.

`push-public` will push to the docker hub.

References
~~~~~~~~~~~~~~~~~~~~~


Docker best practices

https://docs.docker.com/engine/userguide/eng-image/dockerfile\_best-practices/
https://github.com/lwieske/dockerfiles-java-8/blob/master/Dockerfile.slim
https://docs.openshift.com/enterprise/3.0/creating\_images/guidelines.html#general-docker-guidelines
