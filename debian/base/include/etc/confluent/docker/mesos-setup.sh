#!/usr/bin/env bash

if [ -n $MESOS_SANDBOX ] && [ -a $MESOS_SANDBOX/.ssl/scheduler.crt ] && [ -a $MESOS_SANDBOX/.ssl/scheduler.key ]; then
    openssl pkcs12 -export -in $MESOS_SANDBOX/.ssl/scheduler.crt -inkey $MESOS_SANDBOX/.ssl/scheduler.key \
                -out /tmp/keypair.p12 -name keypair \
                -CAfile $MESOS_SANDBOX/.ssl/ca-bundle.crt -caname root -passout pass:export

    keytool -importkeystore \
            -deststorepass changeit -destkeypass changeit -destkeystore /tmp/kafka-keystore.jks \
            -srckeystore /tmp/keypair.p12 -srcstoretype PKCS12 -srcstorepass export \
            -alias keypair

    keytool -import \
            -trustcacerts \
            -alias root \
            -file $MESOS_SANDBOX/.ssl/ca-bundle.crt \
            -storepass changeit \
            -keystore /tmp/kafka-truststore.jks -noprompt


    if [ "$KERBEROS_ENABLED" = "true" ]; then
        export KAFKAREST_OPTS="-Djava.security.auth.login.config=/tmp/client-jaas.conf -Djava.security.krb5.conf=/tmp/krb5.conf"
    fi
fi
