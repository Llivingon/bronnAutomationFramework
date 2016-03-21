import ast
from datetime import datetime
import mysql.connector
import config
from MySQLdb import escape_string as thwart

class PyATF:
    def _updateDB(self, sqlCommand):
        try:
            cnx = mysql.connector.connect(user=config.PyATFDBUserName, password=config.PyATFDBPassword, host = config.PyATFDBHost, database=config.PyATFDBSchema)
            cur = cnx.cursor()
            cur.execute(sqlCommand)
        finally:
            cnx.commit()
            cur.close()
            cnx.close()

    def _queryDB(self, sqlCommand):
        try:
            cnx = mysql.connector.connect(user=config.PyATFDBUserName, password=config.PyATFDBPassword, host = config.PyATFDBHost, database=config.PyATFDBSchema)
            cur = cnx.cursor()
            cur.execute(sqlCommand)
            result = cur.fetchall()
        finally:
            cur.close()
            cnx.close()
        return result

    def fetchTestCases(self):
        testData = []
        i = 0
        results = self._queryDB("Select TestCaseId, SuiteName, TestMethodName, `Params` from TestCases where Deprecated=0 ")
        totalTests = len(results)
        while i <totalTests:
            individualTestData = []
            individualTestData.append(results[i][1].decode('unicode_escape').encode('ascii','ignore')) #SuiteName
            individualTestData.append(results[i][2].decode('unicode_escape').encode('ascii','ignore')) #TestMethodName
            argumentsList = results[i][3] #Params
            argumentsList = ast.literal_eval(argumentsList)
            argumentsList = [n.strip() for n in argumentsList]
            argumentsList.insert(0,results[i][0])
            individualTestData.append(argumentsList) #TestcaseID as first argument
            testData.append(individualTestData)
            i = i+1
        return testData

    def createTestRunId(self, summary="", logfile="NA"):
        currenttime = str(datetime.now())[:19]
        self._updateDB("INSERT into `TestRuns`(`Timestamp`, `LogFile`, `Summary`) VALUES ('%s', '%s', '%s')"%(currenttime, logfile,summary))
        return self._queryDB("SELECT RunId from `TestRuns` where `Timestamp` LIKE '%s'"%currenttime)[0][0]

    def insertTestRunQueue(self, runId, testIds, userId):
        insertValues = ""
        for testId in testIds:
            insertValues = insertValues+"(%d, %d, %d, 'InProgress'),"%(runId, testId, userId)
        self._updateDB("INSERT into TestResults (`RunId`, `TestCaseId`, `UserId`, `Result`) VALUES %s"%insertValues[:-1])

    def updateFailures(self, runId, testIds):
        for testId in testIds:
            self._updateDB("UPDATE TestResults SET Result = 'Fail' WHERE TestCaseId = %d and RunId =%s" %(testId, runId))

    def updateErrors(self, runId, testIds):
        for testId in testIds:
            self._updateDB("UPDATE TestResults SET Result = 'Timeout' WHERE TestCaseId = %d and RunId =%s" %(testId, runId))

    def updateSuccess(self, runId, testIds):
        currenttime = str(datetime.now())[:19]
        for testId in testIds:
            self._updateDB("UPDATE TestResults SET Result = 'Pass' WHERE TestCaseId = %d and RunId =%s" %(testId, runId))
            self._updateDB("UPDATE TestRuns SET EndTimestamp = '%s' where RunId = %s"%(currenttime, runId))

    def fetchUserDetails(self, userId):
        userDetails=[]
        try:
            results = self._queryDB("Select UserName, Email from Users where UserId=%s" %userId)
            userDetails.append(thwart(results[0][0]))
            userDetails.append(thwart(results[0][1]))
            return userDetails
        except:
            return ['laradh001c','lingesh_aradhya@cable.comcast.com']