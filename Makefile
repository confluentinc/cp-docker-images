# You can override vars like REPOSITORY in a local.make file
-include local.make

# Bump this on subsequent build, reset on new version or public release. Inherit $BUILD_NUMBER on Jenkins.
BUILD_NUMBER ?= 1

CONFLUENT_MAJOR_VERSION ?= 3
CONFLUENT_MINOR_VERSION ?= 3
CONFLUENT_PATCH_VERSION ?= 0

CONFLUENT_VERSION ?= ${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}.${CONFLUENT_PATCH_VERSION}

KAFKA_VERSION ?= 0.11.0.0

COMPONENTS := base zookeeper kafka kafka-rest schema-registry kafka-connect-base kafka-connect enterprise-control-center kafkacat enterprise-replicator enterprise-kafka kafka-streams-examples
COMMIT_ID := $(shell git rev-parse --short HEAD)
MYSQL_DRIVER_VERSION := 5.1.39

# Set this variable externally to point at a different repo, such as when building SNAPSHOT images.
CONFLUENT_PACKAGES_REPO ?= http://packages.confluent.io

# Set to false for public releases
ALLOW_UNSIGNED ?= false

REPOSITORY ?= confluentinc

VERSION ?= ${CONFLUENT_VERSION}-${BUILD_NUMBER}

# Packaging semver labels for deb and rpm snapshot packaging, if needed.
CONFLUENT_DEB_LABEL ?=
CONFLUENT_RPM_LABEL ?=

clean-containers:
	for container in `docker ps -aq -f label=io.confluent.docker.testing=true` ; do \
        echo "\nRemoving container $${container} \n========================================== " ; \
				docker rm -f $${container} || exit 1 ; \
  done
	# Remove dangling volumes
	docker volume ls -q -f dangling=true | xargs docker volume rm || true;

clean-images:
	for image in `docker images -q -f label=io.confluent.docker.build.number | uniq` ; do \
        echo "Removing image $${image} \n==========================================\n " ; \
				docker rmi -f $${image} || exit 1 ; \
  done

debian/base/include/etc/confluent/docker/docker-utils.jar:
	mkdir -p debian/base/include/etc/confluent/docker
	cd java \
	&& mvn clean compile package assembly:single -DskipTests \
	&& cp target/docker-utils-${CONFLUENT_VERSION}-jar-with-dependencies.jar ../debian/base/include/etc/confluent/docker/docker-utils.jar \
	&& cd -

build-debian: debian/base/include/etc/confluent/docker/docker-utils.jar
	for component in ${COMPONENTS} ; do \
		echo "\n\nBuilding $${component} \n==========================================\n " ; \
		if [ "$${component}" = "base" ]; then \
			BUILD_ARGS="--build-arg ALLOW_UNSIGNED=${ALLOW_UNSIGNED} --build-arg CONFLUENT_PACKAGES_REPO=${CONFLUENT_PACKAGES_REPO}" ; \
		else \
			BUILD_ARGS=""; \
		fi; \
		for type in "" rpm; do \
			DOCKER_FILE="debian/$${component}/Dockerfile"; \
			COMPONENT_NAME=$${component}; \
			if [ "$${type}" = "rpm" ]; then \
				COMPONENT_NAME="rpm-$${component}"; \
				DOCKER_FILE="$${DOCKER_FILE}.rpm"; \
				SEMVER_LABEL=${CONFLUENT_RPM_LABEL}; \
			else \
				SEMVER_LABEL=${CONFLUENT_DEB_LABEL}; \
			fi; \
			if [ -a "$${DOCKER_FILE}" ]; then \
				docker build --build-arg KAFKA_VERSION=${KAFKA_VERSION} --build-arg SEMVER_LABEL=${SEMVER_LABEL} --build-arg CONFLUENT_MAJOR_VERSION=${CONFLUENT_MAJOR_VERSION} --build-arg CONFLUENT_MINOR_VERSION=${CONFLUENT_MINOR_VERSION} --build-arg CONFLUENT_PATCH_VERSION=${CONFLUENT_PATCH_VERSION} --build-arg COMMIT_ID=${COMMIT_ID} --build-arg BUILD_NUMBER=${BUILD_NUMBER} $${BUILD_ARGS} -t ${REPOSITORY}/cp-$${COMPONENT_NAME}:latest -f $${DOCKER_FILE} debian/$${component} || exit 1 ; \
				docker tag ${REPOSITORY}/cp-$${COMPONENT_NAME}:latest ${REPOSITORY}/cp-$${COMPONENT_NAME}:latest  || exit 1 ; \
				docker tag ${REPOSITORY}/cp-$${COMPONENT_NAME}:latest ${REPOSITORY}/cp-$${COMPONENT_NAME}:${CONFLUENT_VERSION} || exit 1 ; \
				docker tag ${REPOSITORY}/cp-$${COMPONENT_NAME}:latest ${REPOSITORY}/cp-$${COMPONENT_NAME}:${VERSION} || exit 1 ; \
				docker tag ${REPOSITORY}/cp-$${COMPONENT_NAME}:latest ${REPOSITORY}/cp-$${COMPONENT_NAME}:${COMMIT_ID} || exit 1 ; \
			fi; \
		done \
	done

build-test-images:
	for component in `ls tests/images` ; do \
		echo "\n\nBuilding $${component} \n==========================================\n " ; \
		docker build -t ${REPOSITORY}/cp-$${component}:latest tests/images/$${component} || exit 1 ; \
		docker tag ${REPOSITORY}/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:latest || exit 1 ; \
		docker tag ${REPOSITORY}/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${CONFLUENT_VERSION} || exit 1 ; \
		docker tag ${REPOSITORY}/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${VERSION} || exit 1 ; \
		docker tag ${REPOSITORY}/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${COMMIT_ID} || exit 1 ; \
	done

tag-remote:
ifndef DOCKER_REMOTE_REPOSITORY
	$(error DOCKER_REMOTE_REPOSITORY must be defined.)
endif
	for image in `docker images -f label=io.confluent.docker.build.number -f "dangling=false" --format "{{.Repository}}:{{.Tag}}"` ; do \
        echo "\n Tagging $${image} as ${DOCKER_REMOTE_REPOSITORY}/$${image#*/}"; \
        docker tag $${image} ${DOCKER_REMOTE_REPOSITORY}/$${image#*/}; \
  done

push-private: clean build-debian build-test-images tag-remote
ifndef DOCKER_REMOTE_REPOSITORY
	$(error DOCKER_REMOTE_REPOSITORY must be defined.)
endif
	for image in `docker images -f label=io.confluent.docker.build.number -f "dangling=false" --format "{{.Repository}}:{{.Tag}}" | grep $$DOCKER_REMOTE_REPOSITORY` ; do \
        echo "\n Pushing $${image}"; \
        docker push $${image}; \
  done

push-public: clean build-debian
	for component in ${COMPONENTS} ; do \
		echo "\n Pushing cp-$${component}  \n==========================================\n "; \
		docker push ${REPOSITORY}/cp-$${component}:latest || exit 1; \
		docker push ${REPOSITORY}/cp-$${component}:${VERSION} || exit 1; \
		docker push ${REPOSITORY}/cp-$${component}:${CONFLUENT_VERSION} || exit 1; \
  done

clean: clean-containers clean-images
	rm -rf debian/base/include/etc/confluent/docker/docker-utils.jar

venv: venv/bin/activate
venv/bin/activate: tests/requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur tests/requirements.txt
	touch venv/bin/activate

test-docker-utils:
	mkdir -p ../debian/base/include/etc/confluent/docker
	cd java \
	&& mvn clean compile package assembly:single \
	&& src/test/bin/cli-test.sh \
	&& cp target/docker-utils-${CONFLUENT_VERSION}-jar-with-dependencies.jar ../debian/base/include/etc/confluent/docker/docker-utils.jar \
	&& cd -

test-build: venv clean build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_build.py -v

test-zookeeper: venv clean-containers build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_zookeeper.py -v

test-kafka: venv clean-containers build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka.py -v

test-schema-registry: venv clean-containers build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_schema_registry.py -v

test-kafka-rest: venv clean-containers build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka_rest.py -v

tests/fixtures/debian/kafka-connect/jars/mysql-connector-java-${MYSQL_DRIVER_VERSION}-bin.jar:
	mkdir -p tests/fixtures/debian/kafka-connect/jars
	curl -k -SL "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-${MYSQL_DRIVER_VERSION}.tar.gz" | tar -xzf - -C tests/fixtures/debian/kafka-connect/jars --strip-components=1 mysql-connector-java-${MYSQL_DRIVER_VERSION}/mysql-connector-java-${MYSQL_DRIVER_VERSION}-bin.jar

test-kafka-connect: venv clean-containers build-debian build-test-images tests/fixtures/debian/kafka-connect/jars/mysql-connector-java-${MYSQL_DRIVER_VERSION}-bin.jar
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka_connect.py -v

test-enterprise-replicator: venv clean-containers build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_enterprise_replicator.py -v

test-enterprise-kafka: venv clean-containers build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_enterprise_kafka.py -v

test-control-center: venv clean-containers build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_control_center.py -v

test-kafka-streams-examples: venv clean-containers build-debian build-test-images
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka_streams_examples.py -v

test-all: \
	venv \
	clean \
	test-docker-utils \
	build-debian \
	build-test-images \
	test-build \
	test-zookeeper \
	test-kafka \
	test-kafka-connect \
	test-enterprise-replicator \
	test-schema-registry \
	test-kafka-rest \
	test-control-center \
	test-kafka-streams-examples
