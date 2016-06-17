VERSION := 3.0.0

COMPONENTS := base zk

build-debian:
	for component in ${COMPONENTS} ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build -t confluentinc/$${component}:${VERSION} debian/$${component} || exit 1 ; \
				docker tag confluentinc/$${component}:${VERSION} confluentinc/$${component}:latest || exit 1 ; \
  done
