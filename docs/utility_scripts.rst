Utility scripts
----------------

Docker Utility Belt (dub)
~~~~~~~~~~~~~~~~~~~~~~~~

1. Template

	.. sourcecode:: bash

		usage: dub template [-h] input output
		
		Generate template from env vars.
		
		positional arguments:
		  input       Path to template file.
		  output      Path of output file.
	
2. ensure

	.. sourcecode:: bash

		usage: dub ensure [-h] name

		Check if env var exists.
		
		positional arguments:
		  name        Name of env var.
		  
3. wait
		
	.. sourcecode:: bash

		usage: dub wait [-h] host port timeout

		wait for network service to appear.
		
		positional arguments:
		  host        Host.
		  port        Host.
		  timeout     timeout in secs.

4. path

	.. sourcecode:: bash

		usage: dub path [-h] path {writable,readable,executable,exists}

		Check for path permissions and existence.
		
		positional arguments:
		  path                  Full path.
		  {writable,readable,executable,exists} One of [writable, readable, executable, exists].


Confluent Platform Utility Belt (cub)
~~~~~~~~~~~~~~~~~~~~~~~~

1. zk-ready

	.. sourcecode:: bash

		usage: cub zk-ready [-h] connect_string timeout retries wait

		Check if ZK is ready.
		
		positional arguments:
		  connect_string  Zookeeper connect string.
		  timeout         Time in secs to wait for service to be ready.
		  retries         No of retries to check if leader election is complete.
		  wait            Time in secs between retries

2. kafka-ready

	Used for checking if Kafka is ready.

	.. sourcecode:: bash

		usage: cub kafka-ready [-h] connect_string min_brokers timeout retries wait
		
		positional arguments:
		  connect_string  Zookeeper connect string.
		  min_brokers     Minimum number of brokers to wait for
		  timeout         Time in secs to wait for service to be ready.
		  retries         No of retries to check if leader election is complete.
		  wait            Time in secs between retries

3. sr-ready
	
	Used for checking if the Schema Registry is ready.  If you have multiple Schema Registry nodes, you may need to check their availability individually.  

	.. sourcecode:: bash

		usage: cub sr-ready [-h] host port timeout
		
		positional arguments:
		  host  Hostname for Schema Registry.
		  port     Port for Schema Registry.
		  timeout		Time in secs to wait for service to be ready.

3. kr-ready
	
	Used for checking if the REST Proxy is ready.  If you have multiple REST Proxy nodes, you may need to check their availability individually.

	.. sourcecode:: bash

		usage: cub kr-ready [-h] host port timeout
		
		positional arguments:
		  host  Hostname for REST Proxy.
		  port     Port for REST Proxy.
		  timeout         Time in secs to wait for service to be ready.
