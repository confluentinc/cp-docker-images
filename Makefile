VERSION := 3.0.0

COMPONENTS := base kafka

build-debian:
	for component in ${COMPONENTS} ; do \
        echo "\n\nBuilding $${component} \n==========================================\n " ; \
				docker build -t confluentinc/$${component}:${VERSION} debian/$${component} || exit 1 ; \
  done
