VERSION := 3.0.0

COMPONENTS := base zookeeper kafka kafka-rest schema-registry kafka-connect control-center
COMMIT_ID := $(shell git rev-parse --short HEAD)
MYSQL_DRIVER_VERSION := 5.1.39


REPOSITORY := confluentinc
#	REPOSITORY := <your_personal_repo>

clean-containers:
	for container in `docker ps -aq -f label=io.confluent.docker.testing=true` ; do \
        echo "\nRemoving container $${container} \n========================================== " ; \
				docker rm -f $${container} || exit 1 ; \
  done

clean-images:
	for image in `docker images -q -f label=io.confluent.docker | uniq` ; do \
        echo "Removing image $${image} \n==========================================\n " ; \
				docker rmi -f $${image} || exit 1 ; \
  done

build-debian:
	# We need to build images with confluentinc namespace so that dependent image builds dont fail
	# and then tag the images with REPOSITORY namespace
	for component in ${COMPONENTS} ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build --build-arg COMMIT_ID=$${COMMIT_ID} --build-arg BUILD_NUMBER=$${BUILD_NUMBER}  -t confluentinc/cp-$${component}:latest debian/$${component} || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:latest  || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${VERSION} || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${COMMIT_ID} || exit 1 ; \
  done

build-test-images:
	for component in `ls tests/images` ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build -t confluentinc/cp-$${component}:latest tests/images/$${component} || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:latest || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${VERSION} || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${COMMIT_ID} || exit 1 ; \
  done

tag-remote:
ifndef DOCKER_REMOTE_REPOSITORY
	$(error DOCKER_REMOTE_REPOSITORY must be defined.)
endif
	for image in `docker images -f label=io.confluent.docker -f "dangling=false" --format "{{.Repository}}:{{.Tag}}"` ; do \
        echo "\n Tagging $${image} as ${DOCKER_REMOTE_REPOSITORY}/$${image}"; \
        docker tag $${image} ${DOCKER_REMOTE_REPOSITORY}/$${image}; \
  done

push-private: clean-container clean-image build-debian build-test-images tag-remote
ifndef DOCKER_REMOTE_REPOSITORY
	$(error DOCKER_REMOTE_REPOSITORY must be defined.)
endif
	for image in `docker images -f label=io.confluent.docker -f "dangling=false" --format "{{.Repository}}:{{.Tag}}" | grep $$DOCKER_REMOTE_REPOSITORY` ; do \
        echo "\n Pushing $${image}"; \
        docker push $${image}; \
  done

push-public: clean build-debian
	for component in ${COMPONENTS} ; do \
        echo "\n Pushing cp-$${component}  \n==========================================\n "; \
        docker push confluentinc/cp-$${component}:latest; \
				docker push confluentinc/cp-$${component}:${VERSION}; \
  done

clean: clean-container clean-image

venv: venv/bin/activate
venv/bin/activate: tests/requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur tests/requirements.txt
	touch venv/bin/activate

test-build: venv clean build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_build.py -v

test-zookeeper: venv clean-container build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_zookeeper.py -v

test-kafka: venv clean-container build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka.py -v

test-schema-registry: venv clean-container build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_schema_registry.py -v

test-kafka-rest: venv clean-container build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka_rest.py -v

tests/fixtures/debian/kafka-connect/jars/mysql-connector-java-${MYSQL_DRIVER_VERSION}-bin.jar:
	mkdir -p tests/fixtures/debian/kafka-connect/jars
	curl -k -SL "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-${MYSQL_DRIVER_VERSION}.tar.gz" | tar -xzf - -C tests/fixtures/debian/kafka-connect/jars --strip-components=1 mysql-connector-java-5.1.39/mysql-connector-java-${MYSQL_DRIVER_VERSION}-bin.jar

test-kafka-connect: venv clean-container build-debian build-test-images tests/fixtures/debian/kafka-connect/jars/mysql-connector-java-${MYSQL_DRIVER_VERSION}-bin.jar
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka_connect.py -v
