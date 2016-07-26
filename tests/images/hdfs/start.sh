#!/bin/bash

set -e


if [ $TYPE = "NAMENODE" ] ; then
	NAMENODE_IP=$(hostname -i)
else
#	NAMENODE_IP=$(getent hosts ${NAMENODE_HOST}| awk '{ print $1 }')
	NAMENODE_IP=${NAMENODE_HOST}
fi

echo "Namenode IP: ${NAMENODE_IP}"
cat <<EOF |  tee $HADOOP_INSTALL/etc/hadoop/core-site.xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
   <property>
        <name>fs.defaultFS</name>
        <value>hdfs://${NAMENODE_IP}:9000/</value>
        <description>NameNode URI</description>
    </property>
    <property>
      <name>hadoop.proxyuser.hduser.hosts</name>
      <value>*</value>
    </property>
    <property>
      <name>hadoop.proxyuser.hduser.groups</name>
      <value>*</value>
    </property>
</configuration>
EOF

cat <<EOF |  tee $HADOOP_INSTALL/etc/hadoop/hdfs-site.xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
 <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///hdfs/data/datanode</value>
        <description>DataNode directory</description>
 </property>
 <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///hdfs/data/namenode</value>
        <description>NameNode directory for namespace and transaction logs storage.</description>
 </property>

  <property>
        <name>dfs.replication</name>
        <value>${DFS_REPLICATION}</value>
  </property>

   <property>
     <name>dfs.permissions.enabled</name>
     <value>false</value>
   </property>

   <property>
        <name>dfs.datanode.use.datanode.hostname</name>
        <value>false</value>
    </property>

    <property>
        <name>dfs.namenode.datanode.registration.ip-hostname-check</name>
        <value>false</value>
    </property>
</configuration>
EOF

cd $HADOOP_HOME

if [ $TYPE = "NAMENODE" ] ; then
    IS_FORMATTED_FILE=/hdfs/data/namenode/IS_FORMATTED
    if [ -f "${IS_FORMATTED_FILE}" ]; then
        echo "Namenode data dir has already been formatted..."
    else
        echo "Formatting Hadoop Namenode ..."
        $HADOOP_INSTALL/bin/hdfs namenode -format -nonInteractive && echo "true" > ${IS_FORMATTED_FILE}
    fi

    echo "Starting Hadoop Namenode ..."
    exec $HADOOP_INSTALL/bin/hdfs namenode

    # try to set HDFS safemode
    # tryCount=1
    # while(($tryCount<=40))
    # do
    #     echo "Get HDFS out of safemode : $tryCount"
    #     sleep 3
    #     #detect whether HDFS name node is started
    #     name_node_process_num=`netstat  -plan | grep 50070 | wc -l`
    #     if [ $name_node_process_num -ge 1 ]; then
    #         $HADOOP_INSTALL/bin/hadoop dfsadmin -safemode leave
    #         echo "done. HDFS has left safemode."
    #         break
    #     fi
    #     let "tryCount++"
    # done

elif [ $TYPE = "DATANODE" ] ; then
    echo "Starting Hadoop Datanode"
    exec $HADOOP_INSTALL/bin/hdfs datanode
elif [ $TYPE = "HTTPFS" ] ; then
    echo "Starting Hadoop HTTPFS"
    export HTTPFS_TEMP=/tmp
    export HTTPFS_LOG=/tmp
cat <<EOF |  tee $HADOOP_INSTALL/etc/hadoop/httpfs-site.xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
      <name>httpfs.proxyuser.hduser.hosts</name>
      <value>*</value>
    </property>
    <property>
      <name>httpfs.proxyuser.hduser.groups</name>
      <value>*</value>
    </property>
</configuration>
EOF
    exec $HADOOP_INSTALL/sbin/httpfs.sh run
fi
