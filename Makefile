VERSION := 3.0.0

COMPONENTS := base zookeeper kafka kafkacat kafka-rest schema-registry

REPOSITORY := confluentinc
#	REPOSITORY := <your_personal_repo>

build-debian:
	for component in ${COMPONENTS} ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build -t ${REPOSITORY}/$${component}:${VERSION} debian/$${component} || exit 1 ; \
				docker tag ${REPOSITORY}/$${component}:${VERSION} ${REPOSITORY}/$${component}:latest || exit 1 ; \
  done


venv: venv/bin/activate
venv/bin/activate: tests/requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur tests/requirements.txt
	touch venv/bin/activate

docker-env:
	$(shell docker-machine env gce)

test-build: venv
	docker images -q | xargs  docker rmi -f
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_build.py -v
	docker images -q | xargs  docker rmi -f

test-zookeeper: venv build-debian
	docker ps -a -q | xargs  docker rm -f
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_zookeeper.py -v

test-kafka: venv build-debian
	docker ps -a -q | xargs  docker rm -f
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka.py -v
