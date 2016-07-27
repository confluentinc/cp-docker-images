VERSION := 3.0.0

COMPONENTS := base zookeeper kafka kafka-rest schema-registry kafka-connect control-center

REPOSITORY := confluentinc
#	REPOSITORY := <your_personal_repo>

clean-container:
	for container in `docker ps -aq -f label=io.confluent.docker.testing=true` ; do \
        echo "\nRemoving container $${container} \n========================================== " ; \
				docker stop -t=5 $${container} && docker rm -f $${container} || exit 1 ; \
  done

clean-image:
	for image in `docker image -q -f label=io.confluent.docker` ; do \
        echo "\nRemoving container $${container} \n========================================== " ; \
				docker rm -f $${container} || exit 1 ; \
  done

build-debian:
	#
	# We need to build images with confluentinc namespace so that dependent image builds dont fail
	# and then tag the images with REPOSITORY namespace
	for component in ${COMPONENTS} ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build -t confluentinc/cp-$${component}:latest debian/$${component} || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:latest  || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${VERSION} || exit 1 ; \
  done

build-test-images:
	for component in `ls tests/images` ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build -t confluentinc/cp-$${component}:latest tests/images/$${component} || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:latest || exit 1 ; \
				docker tag confluentinc/cp-$${component}:latest ${REPOSITORY}/cp-$${component}:${VERSION} || exit 1 ; \
  done

push:
	for component in ${COMPONENTS}; do \
        echo "\n\nPushing ${REPOSITORY}/cp-$${component}:latest to ${REPOSITORY}\n==========================================\n " ; \
				docker push ${REPOSITORY}/cp-$${component}:latest  || exit 1 ; \
				echo "\n\nPushing ${REPOSITORY}/cp-$${component}:${VERSION} to ${REPOSITORY}\n==========================================\n " ; \
				docker push ${REPOSITORY}/cp-$${component}:${VERSION} || exit 1 ; \
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

tests/fixtures/debian/kafka-connect/jars/mysql-connector-java-5.1.39-bin.jar:
	mkdir -p tests/fixtures/debian/kafka-connect/jars
	curl -k -SL "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.39.tar.gz" | tar -xzf - -C tests/fixtures/debian/kafka-connect/jars --strip-components=1 mysql-connector-java-5.1.39/mysql-connector-java-5.1.39-bin.jar

test-kafka-connect: venv clean-container build-debian build-test-images tests/fixtures/debian/kafka-connect/jars/mysql-connector-java-5.1.39-bin.jar
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka_rest.py -v
