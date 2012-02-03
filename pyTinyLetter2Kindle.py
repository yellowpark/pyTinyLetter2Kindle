#
# pyTinyLetter2Kindle.py
# A simple python script that checks a gmail account for a new tinyletter.com newsletter and sends to a Kindle device.
# 
# Checks a gmail account for the latest unseen email message on the approved senders list.
# Grabs the body of the newsletter, adds a few html tags.
# Creates a file and delivers as an email attachment to the Kindle email address.
# Note that the file is not deleted.
#
# This was a coffee break script to push my tiny newsletter subscriptions to Kindle.
# There is no error checking.
# Run the script via crontab as often as you require.
# It should just work if you change a few personal settings for your gmail account.
# I have absolutely no idea if this will work on a different email provider.
# This script is supplied without any warranty whatsoever, in the hope that it will be useful.
#
# By @yellowpark.
#
# This code is free to use under a GNU Lesser General Public License http://www.gnu.org/licenses/lgpl.html.
#

import re
import imaplib
import email
import os
import smtplib
from email.parser import HeaderParser 
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate

def sendEmail(subject):
    print 'sending the email to Kindle'
    
    # change settings below this line
    HOST = 'smtp.gmail.com'
    TO = 'youremail@kindle.com' 
    FROM = 'yoursendingemail@gmail.com'
    USR = 'yoursendingemail@gmail.com'
    PSS = 'YOUR PASSWORD'
    fPath = r'/home/username/kindle/' + subject + '.html' # change the path to the folder location of the script
    # change settings above this line
    
    msg = MIMEMultipart()
    msg["From"] = FROM
    msg["To"] = TO
    msg["Subject"] = subject
    msg['Date']    = formatdate(localtime=True)
 
    # attach a file
    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(fPath,"rb").read() )
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(fPath))
    msg.attach(part)
 
    server = smtplib.SMTP(HOST, 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(USR, PSS)
   
    try:
        failed = server.sendmail(USR, TO, msg.as_string())
        server.close()
    except Exception, e:
        errorMsg = "Unable to send email. Error: %s" % str(e)
	print errorMsg

def checkEmail():

    # change settings below this line    
    HOST = 'imap.gmail.com'
    USR = 'yourgmail@gmail.com'
    PSS = 'YOUR PASSWORD'
    
    print 'checking email'
    
    try:
        mail = imaplib.IMAP4_SSL(HOST)
        mail.login(USR, PSS)
        mail.list()

        # Out: list of "folders" aka labels in gmail.
        mail.select("inbox") # connect to inbox.

        result, data = mail.uid('search', None, "UNSEEN") # search and return uids for unread messages
        
        if data[0] > '': 
	    	latest_email_uid = data[0].split()[-1]
	    	result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
	     	raw_email = data[0][1]
	
		# now we check if the email address is from one of our tiny letter email subscriptions
		msg = HeaderParser().parsestr(data[0][1])
	
		if approvedSenders(msg['From']):
			print 'we found an authorised email!'
			print msg['From']
			print msg['Subject']
			subjectStripped = re.sub('[^A-Za-z0-9]+', '', msg['Subject'])
			mail = email.message_from_string(raw_email)
	
			for part in mail.walk():
	
			  if part.get_content_charset() is None:
			    charset = chardet.detect(str(part))['encoding']
			  else:
			    charset = part.get_content_charset()
	
			  # multipart are just containers, so we skip them
			  if part.get_content_subtype() != 'text/html':
			      print 'multipart'
			      payload = unicode(part.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')
			      print payload
			      continue
			  print '------------------------------------------->'
	
			# Open a file
			print 'Creating the file'
			fPath = r'/home/username/kindle/' + subjectStripped + '.html' # change this to match the path to the containing folder
			
			fo = open(fPath, "w")
			fo.write('<html><head><title>' + subjectStripped + '</title></head><body>')
			fo.write(payload)
			fo.write('</body></html>')
	
			# Close the file
			fo.close()
	
			# send the email to Kindle
			sendEmail(subjectStripped)
		else:
			print 'Unregistered email'
	else:
	        print 'no unseen messages'
	
    except Exception, e:
        errorMsg = "Unable to send email. Error: %s" % str(e)
	print errorMsg
	
def approvedSenders(emailAddress):
    # I happen to subscribe to these newsletters. Replace with your own authorsied email addresses etc
    # this is the email address of the sending newsletter
    approved = False
    if 'rooreynolds@tinyletter.com' in emailAddress or 'robertbrook@tinyletter.com' in emailAddress:
    	approved = True
    return approved


checkEmail()