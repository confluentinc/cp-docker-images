Generate Credentials

You must generate CA certificates (or use yours if you already have one) and then generate a keystore and truststore
for brokers and clients. You can create the certificates script by using the script
(``examples/kafka-cluster-ssl/secrets/create-certs.sh``). For production, use `these scripts <https://github.com/confluentinc/confluent-platform-security-tools>`_ for generating certificates.

For more information about security, see :ref:`security_with_docker`. Make sure that you have OpenSSL and JDK installed.

#.  Navigate to the secrets directory and run the script to create the certificates and answer "yes" to prompts.

    .. codewithvars:: bash

        cd $(pwd)/examples/kafka-cluster-sasl/secrets $$ yes | ./create-certs.sh

#.  Set the environment variable for secrets directory. We will use this later in our commands. Make sure you are in the ``cp-docker-images`` directory.

    .. codewithvars:: bash

        export KAFKA_SASL_SECRETS_DIR=$(pwd)/examples/kafka-cluster-sasl/secrets

    To configure SASL, all your nodes will need to have a proper hostname. It is not advisable to use ``localhost`` as the hostname.

#.  Create an entry in ``/etc/hosts`` with hostname ``quickstart.confluent.io`` that points to ``eth0`` IP.

    Linux Users
        Run the following commands on the Linux host.

        .. codewithvars:: bash

            export ETH0_IP=$(ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')

            echo ${ETH0_IP} quickstart.confluent.io >> /etc/hosts

    MacOS and Windows Users
        SSH into the Docker container and run the following commands as root. You can SSH into the Docker
        Machine VM by running ``docker-machine ssh confluent``.

        .. codewithvars:: bash

            export ETH0_IP=$(ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')

            echo ${ETH0_IP} quickstart.confluent.io >> /etc/hosts