VERSION := 3.0.0

COMPONENTS := base zookeeper kafka kafka-rest schema-registry kafka-connect control-center

REPOSITORY := confluentinc
#	REPOSITORY := <your_personal_repo>

build-debian:
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

venv: venv/bin/activate
venv/bin/activate: tests/requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur tests/requirements.txt
	touch venv/bin/activate

test-build: venv build-debian build-test-images
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
