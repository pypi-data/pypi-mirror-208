import requests
import telnetlib
import sys
from tabulate import tabulate
import pandas as pd
from .rules import setRules
class couchbaseNode:
    def __init__(self,hostName,loginInformation,loginSecret):
        self.hostname=hostName
        self.logininformation=loginInformation
        self.loginsecret=loginSecret
        self.ruleList=setRules()
        self.clusterDefinition=''
        self.clusterScore=100
        self.allBucketHaveAtLeastOneReplica=True
        self.allNodesAreHealthy=True
        self.mdsApplied=True
        self.allBucketPrimaryVbucketGood=True
        self.allBucketsResident=True
        self.allNodesSameVersion=True
        self.swapEnabled=False
        self.memoryQuotaConfigured=True
        self.getClusterName()
        self.getClusterVersion()
        self.getNodesOnCluster()
        self.getRebalance()
        self.getSettings()
        self.getUsersOnCluster()
        self.getXdcrConnections()
        self.prepareBucketData()
        self.calculateMemoryLimit()
        self.generateResults()
        self.takePicture()
        
    def uniqueVersions(list1):
 
    # initialize a null list
        unique_list = []
 
    # traverse for all elements
        for x in list1:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)
        return unique_list
    def updateRule(self,code,result):
        for item in self.ruleList:
            if item["code"] == code and item["result"]!='failed':
                item["result"] = result
        return True
    def getClusterVersion(self):
        try:
            urlForHealth = f"http://{self.hostname}:8091/pools"
            #print(self.hostname)
            
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            self.clusterVersion=resultParsed['implementationVersion']
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)
    def calculateMemoryLimit(self):
        try:
            urlForHealth = f"http://{self.hostname}:8091/nodes/self"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            nodes=resultParsed
            totalMemoryInMB=int(nodes.get('memoryTotal')/(1024 ** 3))
            totalmemoryQuota=int(nodes.get('memoryQuota')/1024)
            if totalmemoryQuota < (0.8 * totalMemoryInMB):
                self.updateRule(code='configuration-01',result='passed')
            else:
                self.updateRule(code='configuration-01',result='failed')
            
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)
    def getNodesOnCluster(self):
        try:
            urlForHealth = f"http://{self.hostname}:8091/pools/nodes"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            nodes=resultParsed.get('nodes')
            nodeList=[]
            for node in nodes:
                swapSpace=node.get('systemStats')['swap_total']
                clusterMember=node.get('clusterMembership')
                healtStatus=node.get('status')
                nodeIp=node.get('hostname')
                services=node.get('services')
                version=node.get('version')
                nodeModel={
                    "nodeIP": nodeIp,
                    "clusterMember":clusterMember,
                    "healtStatus": healtStatus,
                    "services" : services,
                    "swapSpace": swapSpace,
                    "couchbaseVersion":version
                }
                nodeList.append(nodeModel)
                self.clusterNodes=nodeList
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)
    def getUsersOnCluster(self):
        try:
            urlForHealth = f"http://{self.hostname}:8091/settings/rbac/users"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            userList=[]
            for user in resultParsed:
                userModel={
                    "userName": user.get('name')
                }
                userList.append(userModel)
            self.usersOnCluster=userList
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)
    def getClusterName(self):
        try:
            urlForHealth = f"http://{self.hostname}:8091/pools/nodes"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            self.clusterDefinition=resultParsed['clusterName']
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)
    def getRebalance(self):
        try:
            urlForHealth = f"http://{self.hostname}:8091/pools/default/pendingRetryRebalance"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            #print(resultParsed)
            self.rebalanceStatus=resultParsed
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)
    def getXdcrConnections(self):
        try:
            urlForHealth = f"http://{self.hostname}:8091/pools/default/remoteClusters"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            xdcrConnections=[]
            for remote in resultParsed:
                xdcrModel={
                    "xdcrName": remote.get('name'),
                    "xdcrConnectivity": remote.get('connectivityStatus'),
                    "targetNode":remote.get('hostname').split(":")[0]
                }
                xdcrConnections.append(xdcrModel)
            self.xdcrConnections=xdcrConnections
        except Exception as couchbaseBucketException:
            return couchbaseBucketException
    def prepareBucketData(self):
        try:
            bucketDetailReport=[]
            bucketsEndpoint = f"http://{self.hostname}:8091/pools/default/buckets"
            getBucketDetails = requests.get(
                url=bucketsEndpoint, auth=(self.logininformation,self.loginsecret))
            overallBucketData = getBucketDetails.json()
            bucketList=[]
            for bucket in overallBucketData:
                bucketList.append(bucket.get('name'))
                bucketName=bucket.get('name')
                vbucketMap=bucket.get('vBucketServerMap')
                vbucketCount=vbucketMap.get('vBucketMap')
                count=0
                for vbucket in vbucketCount:
                    count=count+1
                # call bucket endpoint with name and collect result
                bucketSpecialPoint = f"http://{self.hostname}:8091/pools/default/buckets/{bucketName}/stats"
                detailedBucket = requests.get(
                    url=bucketSpecialPoint, auth=(self.logininformation,self.loginsecret))
                statReport = detailedBucket.json()
                # collect details
                bucketStats=bucket.get('basicStats')
                avgResident = sum(statReport['op']['samples']['vb_active_resident_items_ratio'])/len(
                            statReport['op']['samples']['vb_active_resident_items_ratio'])
                bucketRecord = {
                    "bucketName": bucketName,
                    "primaryVbucketCount": count,
                    "bucketType": bucket.get('bucketType'),
                    "bucketReplicas": bucket.get('vBucketServerMap').get('numReplicas'),
                    "bucketQuotaPercentage": round(bucketStats.get('quotaPercentUsed'), 1),
                    "bucketItemCount":  round(bucketStats.get('itemCount')),
                    "bucketResidentRatio": avgResident,
                    "bucketDisUsedInMb": round((bucketStats.get("diskUsed"))/1024/1024, 1)
                }
                bucketDetailReport.append(bucketRecord)
            self.buckets=bucketDetailReport
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)
    def prepareIndexData(self):
        try:
            indexEndpoint = f"http://{self.hostname}:9102/api/v1/stats?skipEmpty=true&redact=true&pretty=true"
            getIndexDetails = requests.get(
                url=indexEndpoint, auth=(self.logininformation, self.loginsecret))
            overallIndexData = getIndexDetails.json()
            indexList = []
            for index in overallIndexData:
                indexData=overallIndexData[index]
                indexName=index
                indexItemSize=indexData.get('avg_item_size')
                indexItemCount=indexData.get('items_count')
                indexHitPercent=indexData.get('cache_hit_percent')
                indexResidentPercent=indexData.get('resident_percent')
                indexIBuildPercent=indexData.get('initial_build_progress')
                indexRecord={
                    "indexName": indexName,
                    "indexAverageItemSize": indexItemSize,
                    "indexItemCount": indexItemCount,
                    "indexHitPercent": indexHitPercent,
                    "indexResidentPercent": indexResidentPercent,
                    "indexBuildPercent": indexIBuildPercent
                }
                indexList.append(indexRecord)
            self.indexes=indexList
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)
    

    def getSettings(self):
        try:
            urlForHealth = f"http://{self.hostname}:8091/settings/autoFailover"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            settingsArray=[]
            self.autofailoverEnabled=resultParsed.get('enabled')
            settingModel={
                "configName": 'autofailover',
                "status": resultParsed.get('enabled'),
            }
            settingsArray.append(settingModel)
            urlForHealth = f"http://{self.hostname}:8091/settings/alerts"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            settingModel={
                "configName": 'email-alerting',
                "status": resultParsed.get('enabled'),
            }
            settingsArray.append(settingModel)
            urlForHealth = f"http://{self.hostname}:8091/settings/autoCompaction"
            getNodeDetails = requests.get(
                url=urlForHealth, auth=(self.logininformation, self.loginsecret))
            resultParsed = getNodeDetails.json()
            settingModel={
                "configName": 'auto-compaction',
                "status": resultParsed.get('autoCompactionSettings').get('databaseFragmentationThreshold').get('percentage')
            }
            settingsArray.append(settingModel)
            self.settingsCluster=settingsArray
        except Exception as couchbaseBucketException:
            print(couchbaseBucketException)

    def generateResults(self):
        clusterNodes=self.clusterNodes
        clusterBuckets=self.buckets
        checkResults=[]
        nodeVersions=[]
        if self.autofailoverEnabled==False:
            self.updateRule(code='configuration-05',result='failed')

        else:
            self.updateRule(code='configuration-05',result='passed')
        for node in clusterNodes:
            healtStatus=node.get('healtStatus')
            clusterMember=node.get('clusterMember')
            nodeVersion=node.get('couchbaseVersion')
            swapTotal=node.get('swapSpace')
            if swapTotal > 0:
                self.updateRule(code='configuration-02',result='failed')
            else:
                self.updateRule(code='configuration-02',result='passed')
            if nodeVersion not in nodeVersions:
                nodeVersions.append(nodeVersion)
            mdsControlCount=len(node.get('services'))
            if healtStatus!='healthy' or clusterMember!='active':
                self.updateRule(code='health-01',result='failed')
            else:
                self.updateRule(code='health-01',result='passed')
            if mdsControlCount > 1:
                self.updateRule(code='configuration-04',result='failed')
            else:
                self.updateRule(code='configuration-04',result='passed')
        for bucket in clusterBuckets:
            bucketReplica=bucket.get('bucketReplicas')
            vbucketCount=bucket.get('primaryVbucketCount')
            bucketResident=bucket.get('bucketResidentRatio')
            if bucketReplica==0:
                self.updateRule(code='bucket-02',result='failed')
            elif bucketReplica==3:
                self.updateRule(code='bucket-02',result='passed')
            else:
                self.updateRule(code='bucket-02',result='passed')
            if vbucketCount%1024!=0:
                self.updateRule(code='bucket-03',result='failed')
            else:
                self.updateRule(code='bucket-03',result='passed')
            if bucketResident < 50:
                self.updateRule(code='bucket-01',result='failed')
            else:
                self.updateRule(code='bucket-01',result='passed')
        if len(nodeVersions) > 1:
            self.updateRule(code='configuration-03',result='failed')
        else:
            self.updateRule(code='configuration-03',result='passed')
        self.checkResults=checkResults
    def takePicture(self):
        for item in self.ruleList:
            if item["result"] == "passed":
                item["result"] = u'\u2714' # green checkmark symbol
            else:
                item["result"] = u'\u2718' # red cross mark symbol
        results=self.ruleList
        dataFrameforNodes=pd.DataFrame(results)
        self.formattedOutput=tabulate(dataFrameforNodes, headers = 'keys', tablefmt = 'psql')
        return f''' Finished healtcheck.'''
    