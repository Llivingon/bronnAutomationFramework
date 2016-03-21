CREATE TABLE `Suites` (
  `SuiteId` int(11) NOT NULL,
  `SuiteName` varchar(60) NOT NULL,
  PRIMARY KEY (`SuiteId`),
  UNIQUE KEY `SuiteName` (`SuiteName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `TestCases` (
  `TestCaseId` int(11) NOT NULL,
  `SuiteName` varchar(60) NOT NULL,
  `TestMethodName` varchar(100) NOT NULL,
  `Params` varchar(250) DEFAULT NULL,
  `Deprecated` tinyint(1) DEFAULT '0',
  `Summary` varchar(5000) DEFAULT NULL,
  PRIMARY KEY (`TestCaseId`),
  UNIQUE KEY `Unique Tests` (`SuiteName`,`TestMethodName`,`Params`),
  CONSTRAINT `FK_SuiteNameConstraint` FOREIGN KEY (`SuiteName`) REFERENCES `Suites` (`SuiteName`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `TestRuns` (
  `RunId` int(11) NOT NULL AUTO_INCREMENT,
  `Timestamp` varchar(25) NOT NULL,
  `EndTimestamp` varchar(25) DEFAULT NULL,
  `LogFile` varchar(260) DEFAULT NULL,
  `Summary` varchar(500) DEFAULT 'NA',
  PRIMARY KEY (`RunId`),
  UNIQUE KEY `Timestamp` (`Timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=1190 DEFAULT CHARSET=utf8;


CREATE TABLE `TestResults` (
  `TestResultId` int(11) NOT NULL AUTO_INCREMENT,
  `RunId` int(11) NOT NULL,
  `TestCaseId` int(11) NOT NULL,
  `UserId` int(11) NOT NULL,
  `Result` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`TestResultId`),
  UNIQUE KEY `Unique Test Results` (`TestResultId`,`RunId`,`TestCaseId`),
  KEY `TestResults_ibfk_1` (`RunId`),
  KEY `TestResults_ibfk_2` (`TestCaseId`),
  KEY `TestResults_ibfk_3` (`UserId`),
  CONSTRAINT `TestResults_ibfk_1` FOREIGN KEY (`RunId`) REFERENCES `TestRuns` (`RunId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `TestResults_ibfk_2` FOREIGN KEY (`TestCaseId`) REFERENCES `TestCases` (`TestCaseId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `TestResults_ibfk_3` FOREIGN KEY (`UserId`) REFERENCES `Users` (`UserId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=419876 DEFAULT CHARSET=utf8;


CREATE TABLE `Users` (
  `UserId` int(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(20) NOT NULL,
  `Email` varchar(60) DEFAULT NULL,
  `Password` varchar(100) DEFAULT NULL,
  `Privileges` int(11) DEFAULT '1',
  PRIMARY KEY (`UserId`),
  UNIQUE KEY `UserName` (`UserName`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8;

CREATE VIEW TESTRESULTS AS
select `TestResults`.`RunId` AS `RunID`,`TestRuns`.`Timestamp` AS `Timestamp`,`TestCases`.`TestCaseId` AS `TestCaseId`,`TestResults`.`Result` AS `Result`,`TestCases`.`SuiteName` AS `SuiteName`,`TestCases`.`TestMethodName` AS `TestMethodname`,`TestCases`.`Summary` AS `Summary`,`Users`.`UserName` AS `UserName`,`TestRuns`.`LogFile` AS `LogFile` from (((`TestResults` join `TestRuns`) join `TestCases`) join `Users`) where ((`TestResults`.`RunId` = `TestRuns`.`RunId`) and (`TestResults`.`TestCaseId` = `TestCases`.`TestCaseId`) and (`TestResults`.`UserId` = `Users`.`UserId`)) order by `TestRuns`.`RunId` desc;

CREATE VIEW `TESTRUNSNAPSHOT` AS
select `Run`.`RunId` AS `RunId`,`Run`.`Summary` AS `Summary`,`Run`.`Timestamp` AS `Timestamp`, `Run`.`EndTimestamp` AS `EndTimestamp`,count(`Res`.`RunId`) AS `Counts`,'PASS' AS `PASS` from (`TestRuns` `Run` join `TestResults` `Res`) where ((`Run`.`RunId` = `Res`.`RunId`) and (`Res`.`Result` = 'Pass') and `Run`.`RunId` in (select `TestRuns`.`RunId` from `TestRuns` order by `TestRuns`.`RunId` desc)) group by `Run`.`RunId` union select `Run`.`RunId` AS `RunId`,`Run`.`Summary` AS `Summary`,`Run`.`Timestamp` AS `Timestamp`,`Run`.`EndTimestamp` AS `EndTimestamp`,count(`Res`.`RunId`) AS `Counts`,'FAIL' AS `FAIL` from (`TestRuns` `Run` join `TestResults` `Res`) where ((`Run`.`RunId` = `Res`.`RunId`) and (`Res`.`Result` = 'Fail') and `Run`.`RunId` in (select `TestRuns`.`RunId` from `TestRuns` order by `TestRuns`.`RunId` desc)) group by `Run`.`RunId` union select `Run`.`RunId` AS `RunId`,`Run`.`Summary` AS `Summary`,`Run`.`Timestamp` AS `Timestamp`,`Run`.`EndTimestamp` AS `EndTimestamp`,count(`Res`.`RunId`) AS `Counts`,'Timeout' AS `Timeout` from (`TestRuns` `Run` join `TestResults` `Res`) where ((`Run`.`RunId` = `Res`.`RunId`) and (`Res`.`Result` = 'Timeout') and `Run`.`RunId` in (select `TestRuns`.`RunId` from `TestRuns` order by `TestRuns`.`RunId` desc)) group by `Run`.`RunId`;

INSERT INTO `Suites` VALUES (1, 'Suite1')
INSERT INTO `Suites` VALUES (2, 'Suite2')
INSERT INTO `TestCases` VALUES (1, 'Suite1', 'testcallflow1', ['InputVariable','OutputVariable'],0,'Test 1 Description')
INSERT INTO `TestCases` VALUES (2, 'Suite1', 'testcallflow2', ['InputVariable','OutputVariable'],0,'Test 2 Description')
INSERT INTO `TestCases` VALUES (3, 'Suite2', 'testcallflow1', ['InputVariable','OutputVariable'],0,'Test 1 Description')
INSERT INTO `TestCases` VALUES (4, 'Suite2', 'testcallflow2', ['InputVariable','OutputVariable'],0,'Test 2 Description')
