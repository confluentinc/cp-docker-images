FROM debian:jessie

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER
LABEL io.confluent.docker=true

WORKDIR /build
ENV VERSION=1.3.0-1

ENV BUILD_PACKAGES="build-essential cmake python git curl zlib1g-dev"
RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
            $BUILD_PACKAGES \
            libsasl2-dev \
            libssl-dev \
            openssl \
            libsasl2-modules-gssapi-mit \
            krb5-user \
            krb5-config \
    && git clone https://github.com/edenhill/kafkacat \
    && cd kafkacat \
    && git checkout tags/debian/$VERSION \
    && ./bootstrap.sh \
    && make install \
    && cd .. && rm -rf kafkacat-debian-$VERSION \
    && apt-get remove --purge -y $BUILD_PACKAGES \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["kafkacat"]
