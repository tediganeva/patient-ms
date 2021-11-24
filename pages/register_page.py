from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# import the Register class.
from store.register import Register

# import the app.
from ehealthApp import *


class RegisterPages(QMainWindow):
    """ Handles registering into the system.

    This class will manage user registration into the application. If registration was successful
    the user will be redirected back to the main application page.

    Attributes:
        ui (list): a list of UI components that update the visual state of the application.
    """

    def __init__(self, ui):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit from QMainWindow library.
        super().__init__()

        # assign the ui component as an internal variable to get access to visual update features.
        self.ui = ui

        # Creating a Timer for use in redirects
        self.myTimer = QTimer()

        # visual update
        self.ui.page_stackedWidget.setCurrentIndex(1)
        self.ui.back_page_pushButton.show()
        self.ui.fields_error_label.hide()

        # masking the password field.
        self.ui.Password_lineEdit.setEchoMode(QLineEdit.Password)
        self.ui.Confirm_pass_lineEdit.setEchoMode(QLineEdit.Password)

        # hook up button clicks to class methods.
        self.ui.back_page_pushButton.clicked.connect(self.BackLogin)
        self.ui.Register_insert_button.clicked.connect(self.RegisterSuccess)


    def RegisterSuccess(self):
        # create a new instance of the register class.
        new_register = Register.create_registration()

        # define top level error used for the
        err = 'Please fill in all fields before clicking REGISTER! \n\n'
        self.ui.fields_error_label.setStyleSheet('color: rgb(201, 22, 102)')

        # align text in a label https://stackoverflow.com/questions/24965060/how-to-align-qlabel-text-to-labels-right-edge
        self.ui.fields_error_label.setAlignment(QtCore.Qt.AlignHCenter)

        # check that the values are not empty
        if (self.ui.ConsentcheckBox.isChecked() is False
                or (self.ui.GPradioButton.isChecked() is False and self.ui.PatientradioButton.isChecked() is False)
                or self.ui.LocationcomboBox.currentText() == 'Choose...'
                or self.ui.FN_lineEdit.text().strip() == ''
                or self.ui.LN_lineEdit.text().strip() == ''
                or self.ui.email_lineEdit.text().strip() == ''
                or self.ui.Password_lineEdit.text().strip() == ''
                or self.ui.Confirm_pass_lineEdit.text().strip() == ''
                or self.ui.Phone_num_lineEdit.text().strip() == ''
                or self.ui.address_lineEdit.text().strip() == ''):
            self.ui.fields_error_label.setText(err)
            self.ui.fields_error_label.show()

        elif new_register.checkEmail(self.ui.email_lineEdit.text().strip()) is None:
            self.ui.fields_error_label.setText('Invalid EMAIL!')
            self.ui.fields_error_label.show()

        # if the email already exists in the database show the user a warning.
        elif new_register.email_already_exists(new_register, self.ui.email_lineEdit.text().strip()) == True:
            self.ui.fields_error_label.setText('Email already exists!')
            self.ui.fields_error_label.show()

        # if the password is not formatted correctly (5-10 alphanumeric characters) show the user a warning
        elif new_register.checkPassword(self.ui.Password_lineEdit.text()) is None:
            self.ui.fields_error_label.setText('Invalid PASSWORD! Password should contain 5-10 alphanumeric characters.')
            self.ui.fields_error_label.show()

        # if the password does not match show the user a warning.
        elif self.ui.Password_lineEdit.text() != self.ui.Confirm_pass_lineEdit.text():
            self.ui.fields_error_label.setText('The PASSWORDS do not match!')
            self.ui.fields_error_label.show()

        elif new_register.checkPhonenumber(self.ui.Phone_num_lineEdit.text()) is None:
            self.ui.fields_error_label.setText('Invalid PhoneNumber! Should contain 11 digits.')
            self.ui.fields_error_label.show()

        else:
            # put values in variables and register the user into the system.
            firstname = self.ui.FN_lineEdit.text().strip()
            lastname = self.ui.LN_lineEdit.text().strip()
            email = self.ui.email_lineEdit.text().strip()
            password = self.ui.Password_lineEdit.text().strip()
            phone = self.ui.Phone_num_lineEdit.text().strip()
            location = self.ui.LocationcomboBox.currentText().strip()
            address = self.ui.address_lineEdit.text().strip()

            if self.ui.GPradioButton.isChecked():
                role = 1  # GP

            elif self.ui.PatientradioButton.isChecked():
                role = 2  # Patient

            # register the user into the system.
            new_register.submit_registration(new_register, email, password, firstname, lastname, phone, location,
                                             address, role)

            # go to register_success page
            self.ui.page_stackedWidget.setCurrentIndex(2)
            self.ui.back_page_pushButton.hide()

            # start timer to redirect user back to the main application page.
            self.myTimer.start(5000)
            self.myTimer.timeout.connect(self.BackLogin)

            # clear form variables after successful registration.
            del firstname
            del lastname
            del email
            del password
            del phone
            del role
            del location
            del new_register


    def BackLogin(self):
        """ Returns back to the login page and clears the registration form. """

        self.myTimer.stop()
        self.ui.page_stackedWidget.setCurrentIndex(0)
        self.ui.back_page_pushButton.hide()

        # Clear all the register fields:
        self.ui.ConsentcheckBox.setChecked(False)
        if self.ui.GPradioButton.isChecked():
            self.ui.GPradioButton.setAutoExclusive(False)
            self.ui.GPradioButton.setChecked(False)
            self.ui.GPradioButton.setAutoExclusive(True)
        elif self.ui.PatientradioButton.isChecked():
            self.ui.PatientradioButton.setAutoExclusive(False)
            self.ui.PatientradioButton.setChecked(False)
            self.ui.PatientradioButton.setAutoExclusive(True)
        self.ui.LocationcomboBox.setCurrentText('Choose...')
        self.ui.address_lineEdit.setText('')
        self.ui.FN_lineEdit.setText('')
        self.ui.LN_lineEdit.setText('')
        self.ui.email_lineEdit.setText('')
        self.ui.Password_lineEdit.setText('')
        self.ui.Confirm_pass_lineEdit.setText('')
        self.ui.Phone_num_lineEdit.setText('')
