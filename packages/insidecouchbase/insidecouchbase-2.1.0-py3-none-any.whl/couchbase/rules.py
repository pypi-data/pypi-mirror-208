def setRules():
    ruleList=[
    {
        "code": "configuration-01",
        "definition" : "Data Memory Quota Configuration",
        "result":"not_checked",
        "severity": "critical",
        "recommendation" : "Data memory quota can not be greater than %80 of OS memory"
    },
    {
        "code": "configuration-02",
        "definition" : "SWAP Configuration",
        "result":"not_checked",
        "severity": "critical",
        "recommendation" : "SWAP can not be used in production couchbase environments"
    },
    {
        "code": "configuration-03",
        "definition" : "All Nodes are Using Same Couchbase Version",
        "result":"not_checked",
        "severity": "critical",
        "recommendation" : "Different versions of couchbase can not be used inside the same cluster."
    },
    {
        "code": "configuration-04",
        "definition" : "Cluster is Working Wtih MDS Model",
        "result":"not_checked",
        "severity": "critical",
        "recommendation" : "1 Couchbase node has to be use 1 service only."
    },
    {
        "code": "configuration-05",
        "definition" : "Autofailover Enabled",
        "result":"not_checked",
        "severity": "critical",
        "recommendation" : "Autofailover needs to be enabled to achive better HA"
    },
    {
        "code": "health-01",
        "definition" : "All Nodes Up and Running",
        "result":"not_checked",
        "severity": "critical",
        "recommendation" : "All nodes have to be up and joined cluster."
    },
    {
        "code": "bucket-01",
        "definition" : "All Buckets Have Resident Ratio Greater Than %50",
        "result":"not_checked",
        "severity": "medium",
        "recommendation" : "Bucket resident ratio needs to be greater than %50"
    },
    {
        "code": "bucket-02",
        "definition" : "All Buckets Have At Least 1 Replica",
        "result":"not_checked",
        "severity": "critical",
        "recommendation" : "All buckets must have at least one replica to prevent data loss in case of emergency"
    },
    {
        "code": "bucket-03",
        "definition" : "All Buckets Have 1024 Primary Vbucket",
        "result":"not_checked",
        "severity": "critical",
        "recommendation" : "All buckets must carry 1024 primary vbucket."
    }
]
    return ruleList