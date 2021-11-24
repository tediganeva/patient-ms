# import for application control.
import sys

# UI library imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# backend store library
from store.conn import connect_to_database, create_database

# import UI pages
from pages.login_page import *
from pages.register_page import *

from ehealthApp import *
import datetime
import sqlite3
import os


# application setup
app = QApplication(sys.argv)
window = QMainWindow()
ui = Ui_App_GUI()
ui.setupUi(window)

# Connecting to the database AND creating it if it doesn't exist
# (function for conn and cursor already called inside create database):
database_path = os.path.join(os.path.abspath(os.getcwd()), 'store', 'UCLH.db')

if os.path.exists(database_path):
    connect_to_database()
else:
    create_database()


# Window size:
window.setFixedWidth(1081)
window.setFixedHeight(851)
width = window.width()
height = window.height()
halfStW = ui.page_stackedWidget.height() / 2
# window.showFullScreen()

# use alt and f4 to exit full screen
if window.isFullScreen():
    windowCenterH = window.width() / 2
    windowCenterV = window.height() / 2
    ui.page_stackedWidget.setGeometry(windowCenterH - width / 2, windowCenterV - halfStW, ui.page_stackedWidget.width(), ui.page_stackedWidget.height())
    ui.ucl_logo_label.setGeometry((windowCenterV - width / 2 + ui.page_stackedWidget.width()), 0, 400, windowCenterV - halfStW)

# set the app starting page (page index = 0):
ui.page_stackedWidget.setCurrentIndex(0)
ui.back_page_pushButton.hide()
ui.logout_pushButton.hide()
ui.patient_record_back_button.hide()
ui.GP_back_button.hide()
ui.patient_back_button.hide()


# go back button to move between pages.
def go_Back():
    curr_page = ui.page_stackedWidget.currentIndex()

    if (curr_page == 0 
        or curr_page == 1 
        or curr_page == 3):
        ui.page_stackedWidget.setCurrentIndex(0)
        ui.email_login_lineEdit.setText('')
        ui.pass_login_lineEdit.setText('')

    if ui.page_stackedWidget.currentIndex() == 0:
        ui.back_page_pushButton.hide()
        ui.logout_pushButton.hide()
        ui.fields_error_label.hide()


# Render the go back button.
ui.back_page_pushButton.clicked.connect(go_Back)


# Updating the status of past appointments to 4 (GP ACTION REQUIRED) or -4 (CANCELLED BY SYSTEM)
# DEPENDING on whether the appointment was confirmed or still pending
# Update happens as soon as running the app:

# Queries for CONFIRMED PAST appointments
query1_confirmed = """SELECT appointment_id, datetime FROM availability, appointment
    WHERE appointment_status_id = 1 AND availability.availability_id = appointment.availability_id"""
query2_confirmed = """UPDATE appointment SET appointment_status_id = 4 WHERE appointment_id = ?"""


# Queries for PENDING PAST Appointments:
query1_pending = """SELECT appointment_id, datetime FROM availability, appointment
    WHERE appointment_status_id = 0 AND availability.availability_id = appointment.availability_id"""
query2_pending = """UPDATE appointment SET appointment_status_id = -4 WHERE appointment_id = ?"""


def update_appointment_status(query_select, query_update):
    conn = sqlite3.connect('store/UCLH.db')
    cursor = conn.cursor()
    now = datetime.datetime.now()
    now_formatted = now.strftime("%Y-%m-%d %H:%M")

    result = cursor.execute(query_select)
    row = result.fetchall()
    for i in range(len(row)):
        if row[i][1] < now_formatted:
            appointment_id = row[i][0]
            cursor.execute(query_update,
                           (appointment_id,))
    conn.commit()
    conn.close()


# PAST CONFIRMED
update_appointment_status(query1_confirmed, query2_confirmed)
# PAST PENDING
update_appointment_status(query1_pending, query2_pending)


# create memory location that will hold the soon to be instantiated RegisterPages class.
new_registration = None


# NOTE: must call init method when user clicks to go to the register page, to update the UI
# this pattern is used to facilitate that requirement, otherwise UI components do not load.
def go_to_registration():
    global new_registration
    new_registration = RegisterPages(ui)


# user clicks to go to the registration page and instatiates the class and ui pages.
ui.RegisterpushButton.clicked.connect(go_to_registration)


# login user created automatically for access to Admin, GP or Patient buttons.
login = LoginPages(ui, window)


# Close the application using the close button:
def close_app():
    window.close()


# Connect the close_app function with the close button:
ui.Close_pushButton.clicked.connect(close_app)

# show the application.
window.show()

# exit the application.
sys.exit(app.exec_())
