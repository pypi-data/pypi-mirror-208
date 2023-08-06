# Couchbase Complete Snapshot 

![](https://upload.wikimedia.org/wikipedia/commons/6/67/Couchbase%2C_Inc._official_logo.png)

InsideCouchbase is a Python library that allows you to analyze and monitor the health of a Couchbase cluster. With InsideCouchbase, you can perform health checks on your Couchbase cluster, check for missing or corrupted data, analyze bucket usage, and monitor cluster settings.

# Features
InsideCouchbase provides the following features:

- Analyze bucket usage: You can analyze the usage of a bucket to see how much data it contains, how many items it has, and how much memory it is using.

- Check cluster health: You can perform a health check on your Couchbase cluster to see if it is functioning properly.

- Check replication status: You can check the replication status of a bucket to see if it is properly replicating data to other nodes.

- Monitor cluster settings: You can monitor the settings of your Couchbase cluster to ensure that they are properly configured.

# Getting Started

1. Install the module

```bash
pip3 install insidecouchbase
```

2. Create a simple python script/module to utilize library.

```python
import couchbase

couchbaseInstance=couchbase.couchbaseNode('127.0.0.1','Administrator','test123')
```
Example results

```
+----+------------------+--------------------------------------------------+----------+--------------------------------------------------------------------------------------+
|    | code             | definition                                       | result   | Recommendation                                                                       |
|----+------------------+--------------------------------------------------+----------+--------------------------------------------------------------------------------------|
|  0 | configuration-01 | Data Memory Quota Configuration                  | ✔        | Data memory quota can not be greater than %70 of OS memory                           |
|  1 | configuration-02 | SWAP Configuration                               | ✘        | SWAP can not be used in production couchbase environments                            |
|  2 | configuration-03 | All Nodes are Using Same Couchbase Version       | ✘        | Different versions of couchbase can not be used inside the same cluster.             |
|  3 | configuration-04 | Cluster is Working Wtih MDS Model                | ✘        | 1 Couchbase node has to be use 1 service only.                                       |
|  4 | configuration-05 | Autofailover Enabled                             | ✘        | Autofailover needs to be enabled to achive better HA                                 |
|  5 | health-01        | All Nodes Up and Running                         | ✔        | All nodes have to be up and joined cluster.                                          |
|  6 | bucket-01        | All Buckets Have Resident Ratio Greater Than %50 | ✔        | Bucket resident ratio needs to be greater than %50                                   |
|  7 | bucket-02        | All Buckets Have At Least 1 Replica              | ✘        | All buckets must have at least one replica to prevent data loss in case of emergency |
|  8 | bucket-03        | All Buckets Have 1024 Primary Vbucket            | ✔        | All buckets must carry 1024 primary vbucket.                                         |
+----+------------------+--------------------------------------------------+----------+--------------------------------------------------------------------------------------+

```

# Supported Couchbase Version

- Couchbase 7.0.X
- Couchbase 7.1.X

# Contributing

If you would like to contribute to InsideCouchbase, please submit a pull request with your changes. Before submitting a pull request, please make sure that your changes are properly tested and documented.

# License
InsideCouchbase is licensed under the MIT license. See the LICENSE file for more information.

