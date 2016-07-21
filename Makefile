VERSION := 3.0.0

<<<<<<< HEAD
COMPONENTS := base zookeeper kafka kafkacat kafka-rest schema-registry kafka-connect
=======
COMPONENTS := base zookeeper kafka kafka-rest schema-registry control-center
>>>>>>> upstream/master

REPOSITORY := confluentinc
#	REPOSITORY := <your_personal_repo>

build-debian:
	for component in ${COMPONENTS} ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build -t ${REPOSITORY}/$${component}:${VERSION} debian/$${component} || exit 1 ; \
				docker tag ${REPOSITORY}/$${component}:${VERSION} ${REPOSITORY}/$${component}:latest || exit 1 ; \
  done

build-test-images:
	for component in `ls tests/images` ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build -t confluentinc/$${component}:${VERSION} tests/images/$${component} || exit 1 ; \
				docker tag confluentinc/$${component}:${VERSION} confluentinc/$${component}:latest || exit 1 ; \
  done

venv: venv/bin/activate
venv/bin/activate: tests/requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur tests/requirements.txt
	touch venv/bin/activate

test-build: venv
	docker ps -a -q | xargs  docker rm -f
	docker images -q | xargs  docker rmi -f
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_build.py -v
	docker images -q | xargs  docker rmi -f

test-zookeeper: venv build-debian build-test-images
	docker ps -a -q | xargs  docker rm -f
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_zookeeper.py -v

test-kafka: venv build-debian build-test-images
	docker ps -a -q | xargs  docker rm -f
	IMAGE_DIR=$(pwd) venv/bin/py.test tests/test_kafka.py -v
