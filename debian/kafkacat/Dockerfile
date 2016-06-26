FROM debian:jessie

WORKDIR /build
ENV VERSION=1.3.0-1

ENV BUILD_PACKAGES="build-essential cmake python git curl zlib1g-dev"
RUN apt-get update -y \
    && apt-get install $BUILD_PACKAGES -y \
    && git clone https://github.com/edenhill/kafkacat \
    && cd kafkacat \
    && git checkout tags/debian/$VERSION \
    && ./bootstrap.sh \
    && make install \
    && cd .. && rm -rf kafkacat-debian-$VERSION \
    && AUTO_ADDED_PACKAGES=`apt-mark showauto` \
    && apt-get remove --purge -y $BUILD_PACKAGES $AUTO_ADDED_PACKAGES \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["kafkacat"]
