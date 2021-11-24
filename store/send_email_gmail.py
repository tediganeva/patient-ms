import sqlite3
import datetime
import smtplib
from email.mime.text import MIMEText
import re
import os


def emails(status, conn, cursor):
    cursor.execute('''
        SELECT datetime, email, first_name, appointment_id 
        FROM appointment, availability, user 
        WHERE appointment.appointment_status_id = ? 
        AND appointment.availability_id = availability.availability_id 
        AND appointment.patient_id = user.user_id''',(status,))

    searchresult = cursor.fetchall()
    print(searchresult)
    i = 0

    while i < len(searchresult):
        m = re.search("(\d{4}-\d{1,2}-\d{1,2})", searchresult[i][0])
        strdate = m.group(1)
        n = re.search("(\d{2}:\d{1,2})", searchresult[i][0])
        strtime = n.group(1)
        now = datetime.datetime.now()

        if (str((now.date() + datetime.timedelta(days = 1))) == str(strdate)):
            sender = 'uclpatientsystem@gmail.com'
            psw = 'qwqiufeng1'
            receiver = searchresult[i][1]
            subject = 'e-Health patient management system'

            if status == 1:
                body = 'Hi\n' + searchresult[i][
                    2] + ':' + '<p>Please don\'t forget you have an appointment tomorrow at ' + strtime + '.</p>' + 'Best,'

            if status == 0:
                body = 'Hi\n' + searchresult[i][
                    2] + ':' + '<p>Your appointment request for tomorrow at ' + strtime + ' has been cancelled by the system because it has not been confirmed by the GP.</p>' + 'Best,'

                cursor.execute('''
                    UPDATE appointment 
                    SET appointment_status_id = -4 
                    WHERE appointment_id = ?''', (searchresult[i][3],))

                conn.commit()

            if status == -1:
                body = 'Hi\n' + searchresult[i][
                    2] + ':' + '<p>Sorry, your appointment for tomorrow at ' + strtime + ' has been cancelled by the GP.</p>' + 'Best,'

            msg = MIMEText(body, 'html', 'utf-8')
            msg['from'] = sender
            msg['to'] = searchresult[i][1]
            msg['subject'] = subject

            # send email
            smtp = smtplib.SMTP('smtp.gmail.com:587')
            smtp.ehlo()
            smtp.starttls()
            smtp.login(sender, psw)  # login
            smtp.sendmail(sender, receiver, msg.as_string())  # send
            smtp.quit()  # quit
            print("send email successed")

        else:
            pass

        i = i + 1
