# UI library imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# import the User class.
from store.user import User

from pages.admin_page import *
from pages.gp_page import *
from pages.patient_page import *

from ehealthApp import *


class LoginPages(QMainWindow):
    """ Handles logging into the application. 
    
    This class will log a user into the application. The class will redirect them to different
    pages depending on the login credentials of the user.

    Attributes:
        ui (list): a list of UI components that update the visual state of the application.
        window (class): UI object for handling current window information.
    """

    def __init__(self, ui, window):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit from QMainWindow library.
        super().__init__()

        # assign the ui component as an internal variable to get access to visual update features.
        self.ui = ui

        # assign window as internal variable to get information about login button user clicked on.
        self.window = window

        self.user = None
        self.credentials = None
        self.user_role = None

        # visual update
        self.ui.AdminpushButton.clicked.connect(self.Login_button)
        self.ui.GPpushButton.clicked.connect(self.Login_button)
        self.ui.PatientpushButton.clicked.connect(self.Login_button)
        self.ui.login_pushButton.clicked.connect(self.Login)
        self.ui.logout_pushButton.clicked.connect(self.Logout)

        # masking the password field.
        self.ui.pass_login_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui.pass_login_lineEdit.setEchoMode(QLineEdit.Password)


    def Login_button(self):
        self.ui.page_stackedWidget.setCurrentIndex(3)
        self.ui.back_page_pushButton.show()
        self.ui.error_login_label.hide()

        sender = self.window.sender()

        # create a correct credentials string to return back to the user if login fails.
        if sender.text() == 'Admin Login':
            self.credentials = 'Admin'
            self.user_role = 0

        elif sender.text() == 'GP Login':
            self.credentials = 'GP'
            self.user_role = 1

        elif sender.text() == 'Patient Login':
            self.credentials = 'Patient'
            self.user_role = 2


    def Login(self):
        # Create a User object and assign it to self.
        self.user = User.create_user()

        # Error label:
        self.ui.error_login_label.setStyleSheet('color: rgb(201, 22, 102)')

        # align text in a label https://stackoverflow.com/questions/24965060/how-to-align-qlabel-text-to-labels-right-edge
        self.ui.error_login_label.setAlignment(QtCore.Qt.AlignHCenter)

        # if user enters an empty field.
        if (self.ui.email_login_lineEdit.text().strip() == ''
        or self.ui.pass_login_lineEdit.text() == ''):
            self.ui.error_login_label.setText('Please fill in all fields!')
            self.ui.error_login_label.show()

            # return early to prevent further login evaluation.
            return

        # attempt to login, class transformation method. If successful, self.user is either an
        # Admin, GP or patient, otherwise self.user is still a User with updated internal state
        # signifying the reason why login was unsuccessful.
        self.user = self.user.login(self.user, self.ui.email_login_lineEdit.text().strip(), self.ui.pass_login_lineEdit.text())

        # check updated internal for whether the email exists.
        if self.user.incorrect_email == True:
            self.ui.error_login_label.setText('Email does not exist!')
            self.ui.error_login_label.show()

        else:
            # check updated internal state for whether the password was entered correctly.
            if self.user.incorrect_password == True:
                text = "Incorrect password! Please use the correct {} credentials.".format(self.credentials)
                self.ui.error_login_label.setText(text)
                self.ui.error_login_label.show()

            # if the users account status is -1 then the user has been deactivated and cannot login.
            elif self.user.user_status_id == -1:
                self.ui.error_login_label.setText('Your account has been DEACTIVATED.')
                self.ui.error_login_label.show()

            # if the users account status is 0 then the users account activation is pending and cannot login yet.
            elif self.user.user_status_id == 0:
                self.ui.error_login_label.setText('Your account is PENDING. Please wait for Admin activation.')
                self.ui.error_login_label.show()

            # if the user has logged in with the incorrect credentials depending on the button pressend.
            elif self.user.user_role_id != self.user_role:
                self.ui.error_login_label.setText(
                    'Please log in with the correct {} credentials'.format(self.credentials))
                self.ui.error_login_label.show()

            # user has successfully logged in and is either an Admin, GP or Patient. Initialise the
            # correct Admin, GP or Patient class to visually update the UI for their respective pages.
            else:
                self.ui.error_login_label.hide()
                self.ui.back_page_pushButton.hide()
                self.ui.email_login_lineEdit.setText('')
                self.ui.pass_login_lineEdit.setText('')

                if self.user.user_role_id == 0:
                    # self.user has now changed to an Admin Class. They can do some Admin stuff now! 📚
                    self.user = AdminPages(self.user, self.ui)

                elif self.user.user_role_id == 1:
                    # self.user has now changed to a GP Class. They can starting fixing people! 🩺
                    self.user = GPPages(self.user, self.ui)

                else:
                    # self.user has now changed to a Patient Class. They can book to see the GP! 😷
                    self.user = PatientPages(self.user, self.ui)


    def Logout(self):
        # resets all user internal state
        del self.user
        del self.credentials
        del self.user_role

        self.ui.page_stackedWidget.setCurrentIndex(0)
        self.ui.logout_pushButton.hide()
        self.ui.patient_back_button.hide()
        self.ui.patient_record_back_button.hide()
        self.ui.GP_back_button.hide()
