import smtplib
import string
import email.MIMEMultipart

SERVER = 'mailrelay.test.com'
FROM = "From@test.com,"
TO= "To@test.com,"

class Emailer:
    def sendemail(self, recipients, subject, content):
        '''recipients=csv'''
        recipients=recipients+","+TO
        content = content + "\n\nThanks,\nQA\n"
        try:
            smtpServer = smtplib.SMTP(SERVER)
            emailData  = string.join(( "From: %s" % FROM, "To: %s" % recipients, "Subject: %s" % subject , "", content), "\r\n")
            recipients = recipients.split(',')
            smtpServer.sendmail(FROM, recipients, emailData)
            smtpServer.quit()
            return 0
        except:
            print ("Couldn't email results!")
            return -1

    def sendIndividualmail(self, recipient, subject, content):
        '''recipient=csv'''
        content = content + "\n\nThanks,"
        try:
            smtpServer = smtplib.SMTP(SERVER)
            emailData  = string.join(( "From: %s" % FROM, "To: %s" % recipient, "Subject: %s" % subject , "", content), "\r\n")
            recipients = []
            recipients.append(recipient)
            smtpServer.sendmail(FROM, recipients, emailData)
            smtpServer.quit()
            return 0
        except:
            print ("Couldn't email results!")
            return -1
