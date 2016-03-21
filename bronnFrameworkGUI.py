
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

import ast
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request, flash, url_for, redirect, session, send_from_directory
from flaskext.mysql import MySQL
from flask.ext.session import Session
from functools import wraps
import gc
import os
import string
import random
from MySQLdb import escape_string as thwart
from passlib.hash import sha256_crypt
import sys
import threading
import time
from wtforms import Form, StringField, PasswordField, BooleanField, validators
sys.path.append("configs")
sys.path.append("facades")
sys.path.append("suites")
import config
import emailmodule

mysql = MySQL()

app = Flask(__name__)
app.secret_key = 'super secret key'
app.debug = False

app.config['MYSQL_DATABASE_USER'] = config.PyATFDBUserName
app.config['MYSQL_DATABASE_PASSWORD'] = config.PyATFDBPassword
app.config['MYSQL_DATABASE_DB'] = config.PyATFDBSchema
app.config['MYSQL_DATABASE_HOST'] = config.PyATFDBHost

mysql.init_app(app)

def testRunner(userId,summary="NA"):
    currentTime = time.strftime("%Y-%m-%d %H:%M")
    scheduledTime=str(datetime.now()+timedelta(minutes=1))[:16]
    while scheduledTime>currentTime:
        print str(userId) +" has scheduled a Job at "+scheduledTime
        time.sleep(20)
        currentTime = time.strftime("%Y-%m-%d %H:%M")
    os.system("cd C:\pyatf_itg\&python testrunner.py --userId %d --summary %s"%(userId,summary))

@app.route("/")
def hello():
    return "<h1>Hello World!</h1>"

@app.route('/user/<name>')
def user(name):
 return '<h1>Hello, %s!</h1>' % name

@app.route('/logs/<path:path>')
def send_js(path):
    return send_from_directory('logs', path)

@app.route('/agent')
def agent():
 user_agent = request.headers.get('User-Agent')
 return '<p>Your browser is %s</p>' %user_agent

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('LoginPage'))
    return wrap

@app.route("/Home/")
def Home():
    return render_template("home.html")

@app.route("/TestCases/")
def Tests():
    testData = []
    i = 0
    cursor = mysql.connect().cursor()
    cursor.execute("select TestCaseId, SuiteName, TestMethodName, Summary, `Params` from TestCases ORDER BY TestCaseId")
    results = cursor.fetchall()
    totalTests = len(results)
    while i <totalTests:
            individualTestData = []
            individualTestData.append(results[i][0]) #TestCaseId
            individualTestData.append(results[i][1].decode('unicode_escape').encode('ascii','ignore')) #SuiteName
            individualTestData.append(results[i][2].decode('unicode_escape').encode('ascii','ignore')) #TestMethodName
            individualTestData.append(results[i][3].decode('unicode_escape').encode('ascii','ignore')) #TestSummary
            argumentsList = results[i][4] #Params
            argumentsList = ast.literal_eval(argumentsList)
            argumentsList = [n.strip() for n in argumentsList]
            individualTestData.append(argumentsList)
            testData.append(individualTestData)
            i = i+1
    return render_template("testcases.html", table = testData)

@app.route("/Results/")
def Results():
    resultsData = []
    passedCount = 0
    failedCount = 0
    i = 0
    cursor = mysql.connect().cursor()
    cursor.execute("Select RunId from TestRuns ORDER BY RunId DESC LIMIT 1")
    runIds = cursor.fetchall()
    runId = runIds[0]
    try:
        if request.args.get('runId') is not None:
            runId = request.args.get('runId')
    except:
        pass
    cursor = mysql.connect().cursor()
    cursor.execute("Select RunID,Timestamp,TestCaseId,SuiteName,TestMethodname,Summary,UserName,Result,LogFile from TESTRESULTS where RunId=%s"%runId)
    results = cursor.fetchall()
    totalTests = len(results)
    while i <totalTests:
            individualTestData = []
            individualTestData.append(results[i][0])#RunID
            individualTestData.append(thwart(results[i][1]))#Timestamp
            individualTestData.append(results[i][2])#TestCaseId
            individualTestData.append(thwart(results[i][3]))#SuiteName
            individualTestData.append(thwart(results[i][4]))#TestMethodname
            individualTestData.append(thwart(results[i][5]))#TestSummary
            individualTestData.append(thwart(results[i][6]))#UserName
            individualTestData.append(results[i][7])#Result
            individualTestData.append(results[i][8])#Logfile
            if results[i][7] =="Pass":
                passedCount = passedCount+1
            else:
                failedCount = failedCount+1
            resultsData.append(individualTestData)
            i = i+1
    passPercentage=round((passedCount+0.00001)/totalTests+0.00001*100,2)#Fix for avoiding Divide by Zero exception
    failPercentage=round((failedCount+0.00001)/totalTests+0.00001*100,2)#Fix for avoiding Divide by Zero exception
    return render_template("testresults.html", table = resultsData, passedCount=passedCount, failedCount=failedCount, totalTests=totalTests, passPercentage=passPercentage, failPercentage=failPercentage)

@app.route("/TestRunner/" , methods=['GET','POST'])
@login_required
def TestRunner():
    userId = session['userId']
    userEmailId = session['emailId']
    try:
        if request.method == "POST":
            if request.form['formId'] == 'atf':
                summary = request.form['RunSummary']
                summary= summary.replace(" ", "")
                t = threading.Thread(target=testRunner, args=(userId, summary))
                t.start()
                flash("Regression Job has been Submitted! Please refer to Results/Email for Updates")
    except Exception as e:
        flash (e)
    return render_template("testrunner.html")

@app.route("/TestSuites/")
def DASServices():
    dasMethods = []
    i = 0
    cursor = mysql.connect().cursor()
    cursor.execute("select DISTINCT SuiteName, TestMethodName, Deprecated from TestCases ORDER BY SuiteName")
    results = cursor.fetchall()
    totalTests = len(results)
    while i <totalTests:
            individualTestData = []
            individualTestData.append(thwart(results[i][0])) #SuiteName
            individualTestData.append((thwart(results[i][1])).replace("test",""))#TestMethodName
            individualTestData.append(results[i][2])#Deprecated
            dasMethods.append(individualTestData)
            i = i+1
    return render_template("testsuites.html", dasMethods = dasMethods)

@app.route("/Analytics/")
@login_required
def Analytics():
    timeLineData = []
    trackerRecordsData = []
    cursor = mysql.connect().cursor()
    cursor.execute("Select DISTINCT TESTRUNSNAPSHOT.RunId, Users.UserName,TESTRUNSNAPSHOT.Timestamp,TESTRUNSNAPSHOT.EndTimestamp from TESTRUNSNAPSHOT, TestResults, Users where (TESTRUNSNAPSHOT.RunId =TestResults.RunId AND Users.UserId = TestResults.UserId AND TESTRUNSNAPSHOT.Timestamp > (SELECT DATE_FORMAT(NOW() - INTERVAL 18 DAY,'%Y-%m-%d'))) ORDER BY TESTRUNSNAPSHOT.RunId")
    results = cursor.fetchall()
    cursor.execute("Select RunId, Summary, Timestamp, EndTimestamp, MAX(IF(PASS = 'PASS',PASS,NULL)) Pass, MAX(IF(PASS = 'PASS', Counts, NULL)) PassCount, MAX(IF(PASS = 'FAIL',PASS,NULL)) Fail, MAX(IF(PASS = 'FAIL', Counts, NULL)) FailCount, MAX(IF(PASS = 'Timeout',PASS,NULL)) Timeout, MAX(IF(PASS = 'Timeout', Counts,NULL)) TimeoutCount FROM TESTRUNSNAPSHOT GROUP BY RunId DESC LIMIT 15")
    results2 = cursor.fetchall()
    i = 0
    totalRecords = len(results2)
    while i <totalRecords:
            individualTestData = []
            individualTestData.append(results2[i][0])#RunID
            individualTestData.append(results2[i][1])#Summary
            individualTestData.append(results2[i][2])#Timestamp
            individualTestData.append(results2[i][3])#EndTimestamp
            individualTestData.append(results2[i][4])#PASS
            individualTestData.append(results2[i][5])#PASSCount
            individualTestData.append(results2[i][6])#FAIL
            individualTestData.append(results2[i][7])#FAILCount
            individualTestData.append(results2[i][8])#Timeout
            individualTestData.append(results2[i][9])#TimeoutCount
            timeLineData.append(individualTestData)
            i = i+1

    totalTrackerRecords = len(results)
    i = 0
    while i <totalTrackerRecords:
            individualTestData = []
            individualTestData.append('"%s-%s", new Date(%s), new Date(%s)' % (results[i][0], thwart(results[i][1]),
                                      (parser.parse(thwart(results[i][2]))-relativedelta(months=1)).strftime('%Y, %m, %d, %H, %M, %S'),
                                      (parser.parse(thwart(results[i][3]))-relativedelta(months=1)).strftime('%Y, %m, %d, %H, %M, %S')))#RunID, #UserName, #Timestamp, #EndTimestamp
            individualTestData = str(individualTestData).replace("'","")
            trackerRecordsData.append(individualTestData)
            trackerRecordsData.append(',')
            i = i+1
    return render_template("analytics.html", timeLineData=timeLineData, leaflet='left', trackerRecordsData=trackerRecordsData)

@app.route("/Login/", methods=['GET','POST'])
def LoginPage():
    error = ''
    try:
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']
            cursor = mysql.connect().cursor()
            cursor.execute("SELECT UserName, Password, UserId, Email FROM Users WHERE UserName = '%s'"%thwart(attempted_username))
            results = cursor.fetchall()
            if len(results) == 0:
                return render_template("login.html", error='Invalid credentials. Try again')
            if attempted_username == thwart(results[0][0]):
                if sha256_crypt.verify(request.form['password'], thwart(results[0][1])):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    session['userId'] = results[0][2]
                    session['emailId'] = results[0][3]
                    flash('You are now logged in:'+str(session['username']))
                    return redirect(url_for('Home'))
                else:
                    error = 'Invalid credentials. Try again'
                    flash(error)
        else:
            return render_template("login.html", error=error)
        gc.collect()
    except Exception as e:
        flash(e)
        return render_template("login.html", error=error)
    return render_template("login.html")

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.Length(min=5, max=20),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice', [validators.DataRequired()])

@app.route("/Register/", methods=['GET','POST'])
def Register():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data))) #form.password.data for plain text
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE UserName = '%s'" %thwart(username))
            results = cursor.fetchall()
            if len(results) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)
            else:
                cursor.execute("INSERT INTO Users (UserName, Password, Email) VALUES ('%s', '%s', '%s')"
                          %(thwart(username), thwart(password), thwart(email)))
                conn.commit()
                flash("Thanks for registering!")
                cursor.execute("SELECT UserName, UserId, Email FROM Users WHERE UserName = '%s'"%thwart(username))
                results = cursor.fetchall()
                session['logged_in'] = True
                session['username'] = username
                session['userId'] = results[0][1]
                session['emailId'] = results[0][2]
                return redirect(url_for('Home'))
        return render_template("register.html", form=form)
    except Exception as e:
        return str(e)

@app.route("/Logout/")
@login_required
def logout():
    try:
        session.clear()
        flash("You have been logged out!")
        gc.collect()
        return redirect(url_for('LoginPage'))
    except Exception as e:
        flash(e)
        return render_template("login.html", error=e)

@app.route("/Forgot/", methods=['GET','POST'])
def forgot():
    error = ''
    try:
        if request.method == "POST":
            attempted_email = request.form['retrieveEmail']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT UserName  FROM Users WHERE Email = '%s'"%thwart(attempted_email))
            results = cursor.fetchall()
            if len(results) == 0:
                flash("Could not find any records with email mentioned!")
                return render_template('forgot.html')
            else:
                try:
                    clearPassword = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(6))
                    encryptedPassword = sha256_crypt.encrypt(clearPassword)
                    cursor.execute("Update Users set Password='%s' where Email='%s'"%(encryptedPassword, thwart(attempted_email)))
                    conn.commit()
                    emailmodule.Emailer().sendIndividualmail(thwart(attempted_email), "Py Units Password Retrieve Utility", "UserName: %s Password: %s"%(results[0][0], clearPassword))
                    flash("New Credentials have been emailed. Please go to Login Page to Login")
                    return render_template('forgot.html')
                except:
                    flash("Credentials could not be emailed")
                return render_template('forgot.html')
    except Exception as e:
        flash(e)
        return render_template("forgot.html", error=e)
    return render_template("forgot.html")

if __name__ == "__main__":
    app.run(port=8080)