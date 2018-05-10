FROM debian:stable

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER
LABEL io.confluent.docker=true

WORKDIR /build
ENV VERSION=1.3.0-1

RUN echo "Building kafkacat ....." \
    && apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y kafkacat \
    && echo "Installing runtime dependencies for SSL and SASL support ...." \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        openssl \
        libssl1.1 \
        libsasl2-2 \
        libsasl2-modules-gssapi-mit \
        krb5-user \
        krb5-config \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["kafkacat"]
