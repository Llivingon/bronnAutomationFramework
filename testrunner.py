# -*- coding: utf-8 -*-
'''
  Bronn Test Framework -
    Created By - Lingesh Aradhya
    License: GNU GPL v3
    Source Control: https://github.com/Llivingon/
    Creation Date: 11 Nov 2015
  Overview -
    Platform - Unix/Windows
    Use Open source scripting language - Python
    Use Open source DB Platform for test reports – MySQL
    Use Open source Web Framework – Flask
    Use Open source Application Server – Any

  Arguments
    UserId
    TestRunSummary
  Background
    Install Python 2.7
    Install Python specific modules
'''

import sys
import unittest
import urllib2
sys.path.append("configs")
sys.path.append("facades")
sys.path.append("suites")
import logging
import dbmodule
import emailmodule
import config
import optparse
import re

from time import gmtime, strftime
from suites.suite1 import Suite1
from suites.suite2 import Suite2


parser = optparse.OptionParser()
parser.add_option('--userId', default=1)
parser.add_option('--summary', default="Test")
options, arguments = parser.parse_args()

USERID = options.userId
SUMMARY = options.summary

ACL=config.ACL_QA

class ATFRunner:
    def __init__(self, summary):
        self.logger, self.logfileName = self.createLoggerObject()
        self.pyATFDbObject = dbmodule.PyATF()
        self.emailObject = emailmodule.Emailer()
        self.runId = self.createRunId(summary)

    def createLoggerObject(self):
        logfile = "Logs%s.log"%(strftime("%Y-%m-%d%H%M%S", gmtime()))
        logfileName = logging.FileHandler('logs/%s' %logfile)
        logger = logging.getLogger('%s' %logfileName)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logfileName.setFormatter(formatter)
        logger.addHandler(logfileName)
        logger.setLevel(logging.DEBUG)
        return logger, logfile

    def createTestSuite(self, userId):
        '''Test suite syntax: suite.addTest(SuiteNam("testName", self.logger, ACL, ["ArgumentsStringsList"]))'''
        testIds = []
        suite = unittest.TestSuite()
        testDatas  = self.pyATFDbObject.fetchTestCases()
        for testCaseData in testDatas:
            getattr(suite,"addTest")(eval(testCaseData[0])(testCaseData[1], self.logger, ACL, testCaseData[2]))
            testIds.append(testCaseData[2][0])
        self.pyATFDbObject.insertTestRunQueue(self.runId, testIds, int(userId))
        self.logger.info("Test Case Ids in Regression Suite: %s"%(str(testIds)))
        return testIds, suite

    def createRunId(self, summary):
        runId = self.pyATFDbObject.createTestRunId(summary, self.logfileName)
        self.logger.info("Run Summary:%s"%str(summary))
        self.logger.info("Run ID Created:%s"%str(runId))
        return runId

    def runRegression(self, testIds, suite):
        self.logger.info("Starting Regression ID:%s"%str(self.runId))
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result

    def updateResults(self, result, testIds):
        failedTests = []
        errorsOrTimeouts = []
        successfulTests = testIds
        self.logger.info("Total Tests Run: %s" %result.testsRun)
        self.logger.info("Result:%s" %str(result))
        for failure in result.failures:
            failedTests.append(failure[0].params[0][0])
            self.logger.info("Fail:TestID,InputArgs:%s,SOAP Response %s" %(failure[0].params[0], str(failure)))
        for error in result.errors:
            errorsOrTimeouts.append(error[0].params[0][0])
            self.logger.info("Error:%s" %str(error))
        if len(failedTests)>0:
            successfulTests = list(set(successfulTests)-set(failedTests))
            self.pyATFDbObject.updateFailures(self.runId, failedTests)
        if len(errorsOrTimeouts)>0:
            successfulTests = list(set(successfulTests)-set(errorsOrTimeouts))
            self.pyATFDbObject.updateErrors(self.runId, list(set(errorsOrTimeouts)))
        if len(successfulTests)>0:
            self.pyATFDbObject.updateSuccess(self.runId, successfulTests)

    def emailResults(self, userId, summary, testIds, result):
        result = str(result).replace("unittest.runner.TextTestResult","").replace("errors","timeouts")
        testLink = "http://"+config.HOST+"/Results/?runId=%s"%self.runId
        userDetails = self.pyATFDbObject.fetchUserDetails(userId)
        subject = "Py Units Results for RunId:%s"%self.runId
        content = "Test Run Summary:%s\n\nEndpoints:%s\n\nRun Link: %s\n\nRun By:%s\n\nTestRunId:%s\n\nResults:%s"%\
                  (summary, "Endpoint",testLink, userDetails[1],self.runId, result)
        self.emailObject.sendemail(userDetails[1], subject, content)


if __name__ == "__main__" or __name__ == "testrunner":
    runner = ATFRunner(SUMMARY)
    testIds, testSuite = runner.createTestSuite(USERID)
    result = runner.runRegression(testIds, testSuite)
    runner.updateResults(result, testIds)
    runner.emailResults(USERID, SUMMARY, testIds, result)