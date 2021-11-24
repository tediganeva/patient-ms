# UI library imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# import helper widgets for UI tables.
from widgets.table_widgets import table_data_settings, table_row_select, table_display_data

# import app.
from ehealthApp import *

# import the Admin.
from store.admin import Admin


class AdminPages(QMainWindow):
    """ AdminPages houses the page view and functionality of an Admin after they log in. 

    Attributes:
        admin (class): an Admin object class that contains methods for an Admin to query the database.
        ui (list): a list of UI components that update the visual state of the application.
    """

    def __init__(self, Admin, ui):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit from QMainWindow library.
        super().__init__()

        # NOTE: must not use "user" because it will be an ambigous method call and will not work.
        # set the internal state variable of Admin to admin class. Inherit all internal state
        self.admin = Admin

        # assign the ui component as an internal variable to get access to visual update features.
        self.ui = ui

        # visual update
        self.ui.Delete_rec_pushButton.hide()
        self.ui.manage_buttonBox.hide()
        self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).setText("Activate")
        self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).setText("Deactivate")
        self.ui.logout_pushButton.show()
        self.ui.page_stackedWidget.setCurrentIndex(4)
        if self.admin.user_status_id == 1:
            self.admin.user_status_id_name = 'ACTIVATED'
        if self.admin.user_role_id == 0:
            self.admin.user_role_id_name = 'ADMIN'
        self.ui.AdminEmail_label.setText('Email: ' + str(self.admin.email))
        self.ui.AdminStatus_label.setText('Status: ' + str(self.admin.user_status_id_name))
        self.ui.AdminRole_label.setText('Role: ' + str(self.admin.user_role_id_name))
        self.ui.manage_id_label.setText('ID: ')
        self.ui.manage_email_label.setText('Email: ')
        self.ui.manage_status_label.setText('Status: ')

        # connect buttons to class methods.
        self.ui.Manage_pushButton.clicked.connect(self.Manage)
        self.ui.manage_records_comboBox.currentIndexChanged.connect(self.Manage_Records)
        self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.activate)
        self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.deactivate)
        self.ui.logout_pushButton.clicked.connect(self.Logout)
        self.ui.Admin_acc_pushButton.clicked.connect(self.AdminAcc)
        self.ui.admin_tableWidget.clicked.connect(self.Selections)
        self.ui.Delete_rec_pushButton.clicked.connect(self.delete_record)
        self.ui.emailConfirmCancel_pushButton.clicked.connect(self.send_emails_not_pending)
        self.ui.emailSystemCancel_pushButton.clicked.connect(self.send_emails_pending)

        # table settings
        table_data_settings(self.ui.admin_tableWidget)


    def Manage(self):
        """ Shows the initial management view for the Admin to manage other user accounts. """

        self.ui.page_stackedWidget.setCurrentIndex(5)

        # set the initial current index of the management dropdown box to 0 (All)
        self.ui.manage_records_comboBox.setCurrentIndex(0)

        # query database and populate admin management table.
        query_result = self.admin.manage_records(self.ui.manage_records_comboBox.currentText())
        table_display_data(self.ui.admin_tableWidget, query_result)


    def Manage_Records(self):
        """ A filter for the Admin to view specific account types and account statuses. """

        self.ui.manage_buttonBox.hide()
        self.ui.Delete_rec_pushButton.hide()

        # clear labels when changing comboBox selection.
        self.ui.manage_id_label.setText('ID: ')
        self.ui.manage_email_label.setText('Email: ')
        self.ui.manage_status_label.setText('Status: ')

        # query database and populate admin management table.
        query_result = self.admin.manage_records(self.ui.manage_records_comboBox.currentText())
        table_display_data(self.ui.admin_tableWidget, query_result)


    def AdminAcc(self):
        """ Button to go back to the main Admin account page and clear all previously selected fields. """

        self.ui.page_stackedWidget.setCurrentIndex(4)
        self.ui.manage_buttonBox.hide()
        self.ui.Delete_rec_pushButton.hide()
        self.ui.manage_id_label.setText('ID: ')
        self.ui.manage_email_label.setText('Email: ')
        self.ui.manage_status_label.setText('Status: ')


    def Selections(self):
        """ Buttons that enable the Activation, Deactivation or Deletion of user accounts. """

        self.ui.Delete_rec_pushButton.show()
        self.ui.manage_buttonBox.show()

        try:
            table_row_select(self.ui.admin_tableWidget,
                             [self.ui.manage_id_label, self.ui.manage_email_label, self.ui.manage_status_label],
                             ID=0, Email=1, Status=7)

            userid_status = self.ui.manage_status_label.text()[8:]

            if userid_status == 'PENDING ACTIVATION':
                self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
                self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)
                self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).setStyleSheet('background-color: rgb(154, 207, 171)')
                self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).setStyleSheet('background-color: rgb(255, 156, 153)')
                self.ui.Delete_rec_pushButton.setEnabled(True)

            elif userid_status == 'ACTIVATED':
                self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
                self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)
                self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).setStyleSheet('background-color: rgb(186, 186, 186)')
                self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).setStyleSheet('background-color: rgb(255, 156, 153)')
                self.ui.Delete_rec_pushButton.setEnabled(True)

            elif userid_status == 'DEACTIVATED':
                self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
                self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
                self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).setStyleSheet('background-color: rgb(154, 207, 171)')
                self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).setStyleSheet('background-color: rgb(186, 186, 186)')
                self.ui.Delete_rec_pushButton.setEnabled(True)

        except Exception as e:
                self.ui.manage_id_label.setText('ID: ')
                self.ui.manage_email_label.setText('Email: ')
                self.ui.manage_status_label.setText('Status: ')
                self.ui.manage_buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
                self.ui.manage_buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
                self.ui.Delete_rec_pushButton.setEnabled(False)


    def delete_record(self):
        """ Deletes a record from the database depending on Admin table selection. """

        userid_to_delete = self.ui.manage_id_label.text()[4:]

        # remove the selected user from the system.
        self.admin.delete_user(userid_to_delete)
        self.Manage_Records()


    def activate(self):
        """ Activates a user account in the database depending on Admin table selection. """

        userid_to_activate = self.ui.manage_id_label.text()[4:]

        # activate selected user.
        self.admin.activate_user(userid_to_activate)
        self.Manage_Records()


    def deactivate(self):
        """ Deactivates a user account in the database depending on Admin table selection. """

        userid_to_deactivate = self.ui.manage_id_label.text()[4:]

        # deactivate selected user.
        self.admin.deactivate_user(userid_to_deactivate)
        self.Manage_Records()


    def send_emails_not_pending(self):
        """ Sends emails to patients for NOT pending next day appointments. """
        self.admin.send_emails_patients("not_pending")


    def send_emails_pending(self):
        """ Sends emails to patients for PENDING next day appointments. """
        self.admin.send_emails_patients("pending")


    def Logout(self):
        """ Logs out the Admin, returning the user to the main login page. """

        # hide logout and back buttons.
        self.ui.logout_pushButton.hide()
        self.ui.back_page_pushButton.hide()

        # go back to login page.
        self.ui.page_stackedWidget.setCurrentIndex(0)
