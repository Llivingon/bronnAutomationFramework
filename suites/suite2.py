import unittest
import time
HEADER = {'content-type': 'text/xml'}


class Suite2(unittest.TestCase):
    def __init__(self, testName, *args):
        super(Suite2, self).__init__(testName)
        self.logger = args[0]
        self.acl = args[1]
        self.params = list(args[2:])

    def setUp(self):
        self.logger.info("Validating: %s"%self._testMethodName)

    def tearDown(self):
        self.logger.debug("Test ID: %s"%self.testId)

    def testcallflow1(self):
        """TestCase:testcallflow1"""
        self.testId = self.params[0][0]
        inputParam = self.params[0][1]
		outputParam = self.params[0][2]
        trackingId = "QA_"+self._testMethodName[4:]+str(time.time()).replace(".","")[8:]
        return "PASS"

    def testcallflow2(self):
        """TestCase:testcallflow2"""
        self.testId = self.params[0][0]
        inputParam = self.params[0][1]
		outputParam = self.params[0][2]
        trackingId = "QA_"+self._testMethodName[4:]+str(time.time()).replace(".","")[8:]
        return "PASS"