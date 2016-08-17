
1. Use different volumes for transaction logs and data for Zookeeper.

2. Use host networking for standalone deployments.

3. Run with restart=always

4. Use external volumes for data



Caveats:

- Not tested on overlay networks
- Snappy + Zulu slowness.
- SASL + Bridged n/w don't work with ZK
