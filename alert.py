from datetime import datetime, timedelta
import time
import smtplib
import webbrowser

sender = "jeromehallett@hotmail.co.uk"
receivers = ["jeromehallett@hotmail.co.uk"]
subject = "Test"
alert_msg = "This is a test e-mail message."
try:
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(sender, receiver, alert_msg)
    print("Successfully sent email")
except SMTPException:
    print("Error: unable to send email")


if temp > temp_thresh and flag != True:
          flag_time = datetime.now()
          flag = True
        if temp > temp_thresh and flag == True:
          if datetime.now() - flag_time > time_thresh:
            print 'alert'
            try:
              smtpObj = smtplib.SMTP('localhost')
              smtpObj.sendmail(sender, receiver, alert_msg)
              print "Successfully sent email"
            except SMTPException:
              print "Error: unable to send email"
        if flag == True and temp < temp_thresh:
          flag_time = None
          flag = False