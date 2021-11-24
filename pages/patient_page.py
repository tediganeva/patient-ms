# UI library imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# import helper widgets for UI tables.
from widgets.table_widgets import table_data_settings, table_row_select, table_goes_blank, table_display_data

# ad-hoc requirements.
import datetime

# import app.
from ehealthApp import *

# import the Patient.
from store.patient import Patient


class PatientPages(QMainWindow):
    """ PatientPages houses the view and functionality of a Patient after they log in. 

    Attributes:
        patient (class): a Patient object class that contains methods for a Patient to query the database.
        ui (list): a list of UI components that update the visual state of the application.
    """

    def __init__(self, Patient, ui):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit from QMainWindow library.
        super().__init__()

        # set the internal state variable of gp to GP class. 
        # NOTE: must not use "user" because it will be an ambigous method call and will not work.
        self.patient = Patient

        # assign the ui component as an internal variable to get access to visual update features.
        self.ui = ui

        # visual update and reset internal data.
        self.ui.delete_appointment_button.hide()
        self.ui.logout_pushButton.show()
        self.ui.page_stackedWidget.setCurrentIndex(12)
        if self.patient.user_role_id == 2:
            self.patient.user_role_id_name = 'PATIENT'
        if self.patient.user_status_id == 1:
            self.patient.user_status_id_name = 'ACTIVATED'
        self.ui.patientEmail_label.setText('Email: ' + str(self.patient.email))
        self.ui.patientRole_label.setText('Role: ' + str(self.patient.user_role_id_name))
        self.ui.patientStatus_label.setText('Status: ' + str(self.patient.user_status_id_name))
        self.ui.locationBox.setCurrentIndex(0)
        self.ui.availability_id_label.setText('availability_id: ')
        self.ui.doctor_id_label.setText('doctor_id: ')
        self.ui.datetime_label.setText('datetime: ')
        self.ui.address_label_2.setText('address: ')
        self.ui.appointment_id_label.setText('appointment_id: ')
        self.ui.datetime_label_2.setText('datetime: ')
        self.ui.appointment_status_label.setText('appointment_status: ')
        self.ui.doctor_email_label.setText('doctor_email: ')
        self.ui.doctor_id.setText('doctor_id: ')
        self.ui.appointment_location.setText('appointment_location: ')
        self.ui.appointment_address.setText('appointment_address: ')
        self.ui.doctor_name.setText('doctor_first_name: ')
        self.ui.doctor_last_name.setText('doctor_last_name: ')
        self.ui.doctor_name_label.setText('doctor_first_name: ')
        self.ui.doctor_last_name_label.setText('doctor_last_name: ')
        self.ui.appointment_id_label_2.setText('appointment_id: ')
        self.ui.datetime_label_3.setText('datetime: ')
        self.ui.doctor_email_label_2.setText('doctor_email: ')
        self.ui.diagnosis_label.setText('diagnosis: ')
        self.ui.prescription_info_label.setText('prescription_info: ')
        self.ui.doctors_comment_label.setText('doctors_comment: ')
        self.ui.fields_error_label_2.hide()
        self.ui.availability_id_label.hide()
        self.ui.doctor_id_label.hide()
        self.ui.SubmitpushButton.hide()
        self.ui.patient_back_button.hide()

        # connect buttons to class methods.
        self.ui.bookButton.clicked.connect(self.Book_Button)
        self.ui.checkAppointmentbutton.clicked.connect(self.Check_Appointment_Button)
        self.ui.checkPrescriptionsbutton.clicked.connect(self.Check_Prescription_Button)
        self.ui.locationBox.currentIndexChanged.connect(self.Change_Location)
        self.ui.appointment_comboBox.currentIndexChanged.connect(self.Search_appointment)
        self.ui.SubmitpushButton.clicked.connect(self.Submit_Button)
        self.ui.availabilityTable.clicked.connect(self.availability_Selections)
        self.ui.check_appointment_widget.clicked.connect(self.appointment_Selections)
        self.ui.delete_appointment_button.clicked.connect(self.delete_appointment)
        self.ui.logout_pushButton.clicked.connect(self.Logout)

        self.ui.view_prescription_table.clicked.connect(self.prescription_selections)
        self.ui.patient_back_button.clicked.connect(self.patient_back)

        # set calender to only allow appointment to be booked at least one day in advance
        date_tomorrow=datetime.date.today() + datetime.timedelta(days = 1)
        self.ui.appointment_date.setMinimumDate(QDate(date_tomorrow.year, date_tomorrow.month, date_tomorrow.day))
        self.ui.appointment_date.clicked.connect(self.Search_Button_date)
        today = datetime.datetime.now()
        formatted_today = QDate(today.year, today.month, today.day)
        self.ui.appointment_date.setSelectedDate(formatted_today)  # clear the date selection to set to current date

        # table settings
        table_data_settings(self.ui.availabilityTable)
        table_data_settings(self.ui.check_appointment_widget)
        table_data_settings(self.ui.view_prescription_table)


    def Book_Button(self):
        """ Button to go to the book appointment page. """

        self.ui.page_stackedWidget.setCurrentIndex(13)
        self.Change_Location()
        self.ui.patient_back_button.show()

        # Display the data for the selected date (today) everytime this button is pressed:
        self.Search_Button_date()


    def Check_Appointment_Button(self):
        """ Display check appointments page where the patient can check their upcoming, pending or past appointments. """

        # navigate to correct page and reset table data.
        self.ui.page_stackedWidget.setCurrentIndex(15)
        self.ui.patient_back_button.show()
        self.ui.delete_appointment_button.hide()
        self.ui.delete_appointment_button.hide()
        self.ui.appointment_id_label.setText('appointment_id: ')
        self.ui.datetime_label_2.setText('datetime: ')
        self.ui.appointment_status_label.setText('appointment_status: ')
        self.ui.doctor_email_label.setText('doctor_email: ')
        self.ui.doctor_id.setText('doctor_id: ')
        self.ui.doctor_name_label.setText('doctor_first_name: ')
        self.ui.doctor_last_name_label.setText('doctor_last_name: ')
        self.ui.appointment_location.setText('appointment_location: ')
        self.ui.appointment_address.setText('appointment_address: ')

        # capture dropdown box state.
        appointment_status = self.ui.appointment_comboBox.currentText()
        now = datetime.datetime.now()

        # make backend query and populate appointment table base on dropdown box selection.
        query_result = self.patient.check_appointments(self.patient.user_id, now, appointment_status)
        table_display_data(self.ui.check_appointment_widget, query_result)


    def Change_Location(self):
        """ Button to change the location of the GP when booking an appointment. """

        # navigate to correct page and reset table data.
        self.ui.SubmitpushButton.hide()
        self.ui.doctor_name.setText('doctor_first_name: ')
        self.ui.doctor_last_name.setText('doctor_last_name: ')
        self.ui.availability_id_label.setText('availability_id: ')
        self.ui.doctor_id_label.setText('doctor_id: ')
        self.ui.datetime_label.setText('datetime: ')
        self.ui.address_label_2.setText('address: ')
        self.ui.fields_error_label_2.hide()

        # reset the table and present a new one when the patient clicks search.
        #table_goes_blank(self.ui.availabilityTable)
        self.Search_Button_date()


    def Search_Button_date(self):
        """ Search GP's availability based on date and location. """

        # navigate to correct page and reset table data.
        self.ui.SubmitpushButton.hide()
        self.ui.fields_error_label_2.hide()
        self.ui.doctor_name.setText('doctor_first_name: ')
        self.ui.doctor_last_name.setText('doctor_last_name: ')
        self.ui.availability_id_label.setText('availability_id: ')
        self.ui.doctor_id_label.setText('doctor_id: ')
        self.ui.datetime_label.setText('datetime: ')
        self.ui.address_label_2.setText('address: ')

        # capture dropdown box state and selected date for appointment.
        GP_location = self.ui.locationBox.currentText()
        date = self.ui.appointment_date.selectedDate()
        availability_date = "{:4d}-{:02d}-{:02d}".format(date.year(), date.month(), date.day())

        # query database and populate gp availability table based on date and location selected.
        query_result = self.patient.search_gp_availability(availability_date, GP_location)
        table_display_data(self.ui.availabilityTable, query_result)


    def Search_appointment(self):
        """ Search upcoming or past appointments based on user selection. """

        # navigate to correct page and reset table data.
        self.ui.delete_appointment_button.hide()
        self.ui.delete_appointment_button.hide()
        self.ui.appointment_id_label.setText('appointment_id: ')
        self.ui.datetime_label_2.setText('datetime: ')
        self.ui.appointment_status_label.setText('appointment_status: ')
        self.ui.doctor_email_label.setText('doctor_email: ')
        self.ui.doctor_id.setText('doctor_id: ')
        self.ui.doctor_name_label.setText('doctor_first_name: ')
        self.ui.doctor_last_name_label.setText('doctor_last_name: ')
        self.ui.appointment_location.setText('appointment_location: ')
        self.ui.appointment_address.setText('appointment_address: ')

        # capture dropdown box state and calculate current time.
        appointment_status = self.ui.appointment_comboBox.currentText()
        now = datetime.datetime.now()

        # query database and populate booked appointments table.
        query_result = self.patient.check_appointments(self.patient.user_id, now, appointment_status)
        table_display_data(self.ui.check_appointment_widget, query_result)


    def Description(self):
        """ Converts patient problem info to plain text. """

        global problem_info
        problem_info = self.ui.problemDescription.toPlainText(self)
        print(problem_info)


    def availability_Selections(self):
        """ Capture patient selection of the availability table. """

        self.ui.SubmitpushButton.show()
        self.ui.fields_error_label_2.hide()
        table_row_select(self.ui.availabilityTable,
                         [self.ui.availability_id_label,  self.ui.doctor_id_label,  self.ui.datetime_label, 
                            self.ui.address_label_2, self.ui.doctor_name, self.ui.doctor_last_name],
                         availability_id=0, doctor_id=1, datetime=2, address=3, doctor_first_name=4, doctor_last_name=5)


    def appointment_Selections(self):
        """ Capture patient selection of the appointments table and changes UI depending on appointment selected. """

        self.ui.delete_appointment_button.show()

        table_row_select(self.ui.check_appointment_widget,
                         [self.ui.appointment_id_label, self.ui.datetime_label_2, self.ui.appointment_status_label, 
                            self.ui.doctor_email_label, self.ui.doctor_id, self.ui.appointment_location, 
                            self.ui.appointment_address, self.ui.doctor_name_label, self.ui.doctor_last_name_label],
                         appointment_id=0, datetime=2, appointment_status=1, doctor_email=3, doctor_id=4, 
                            appointment_location=5, appointment_address=6, doctor_name=7, doctor_last_name=8)

        appointment_status_name = self.ui.appointment_status_label.text()[20:]
        print(appointment_status_name)

        appointment_status = self.ui.appointment_comboBox.currentText()

        if appointment_status == 'new':
            if appointment_status_name == 'PENDING CONFIRMATION' or appointment_status_name == 'CONFIRMED':
                self.ui.delete_appointment_button.setEnabled(True)

            else:
                self.ui.delete_appointment_button.setEnabled(False)

        if appointment_status == 'past':
            self.ui.delete_appointment_button.setEnabled(False)


    def delete_appointment(self):
        """ Cancels a booked appointment with a GP. """

        appointmentid_to_delete = self.ui.appointment_id_label.text()[16:]
        doctor_id = self.ui.doctor_id.text()[11:]
        datetime_to_delete = self.ui.datetime_label_2.text()[10:]
        print(appointmentid_to_delete)

        self.patient.cancel_appointment(appointmentid_to_delete, datetime_to_delete, doctor_id)

        # reset the table labels and reload the table.
        self.ui.appointment_id_label.setText('appointment_id: ')
        self.ui.datetime_label_2.setText('datetime: ')
        self.ui.appointment_status_label.setText('appointment_status: ')
        self.ui.doctor_email_label.setText('doctor_email: ')
        self.ui.doctor_id.setText('doctor_id: ')
        self.ui.doctor_name_label.setText('doctor_first_name: ')
        self.ui.doctor_last_name_label.setText('doctor_last_name: ')
        self.ui.appointment_location.setText('appointment_location: ')
        self.ui.appointment_address.setText('appointment_address: ')
        self.ui.delete_appointment_button.hide()
        self.Search_appointment()


    def Submit_Button(self):
        """ Submits an appointment into the database for the GP to later confirm or remove. """

        availability_id = self.ui.availability_id_label.text()[16:]
        problem_info = self.ui.problemDescription.toPlainText().strip().replace('\n', ';')
        self.ui.fields_error_label_2.setStyleSheet('color: rgb(201, 22, 102)')

        if problem_info == '':
            self.ui.problemDescription.setFocus()
            # self.ui.fields_error_label_2.setText('Please fill in all fields!')
            self.ui.fields_error_label_2.show()
            print("can't submit")

        elif len(problem_info) > 100:
            self.ui.problemDescription.setFocus()
            self.ui.fields_error_label_2.setText('Description too long!')
            self.ui.fields_error_label_2.show()
            print("can't submit")

        else:
            self.ui.problemDescription.clearFocus()
            self.ui.fields_error_label_2.hide()

            # submit appointment booking to the backend for gp to late confirm or cancel.
            self.patient.submit_appointment_booking(availability_id, self.patient.user_id, problem_info)

            self.ui.availability_id_label.setText('availability_id: ')
            self.ui.doctor_id_label.setText('doctor_id: ')
            self.ui.datetime_label.setText('datetime: ')
            self.ui.problemDescription.setPlainText('')
            self.ui.fields_error_label_2.hide()
            self.ui.page_stackedWidget.setCurrentIndex(12)
            self.ui.patient_back_button.hide()

            # Reset table and labels:
            self.ui.doctor_name.setText('doctor_first_name: ')
            self.ui.doctor_last_name.setText('doctor_last_name: ')
            self.ui.availability_id_label.setText('availability_id: ')
            self.ui.doctor_id_label.setText('doctor_id: ')
            self.ui.datetime_label.setText('datetime: ')
            self.ui.address_label_2.setText('address: ')
            table_goes_blank(self.ui.availabilityTable)


    def Check_Prescription_Button(self):
        """ Button to navigate patient to a page where they can check prescriptions. """

        self.ui.page_stackedWidget.setCurrentIndex(14)
        self.ui.patient_back_button.show()

        """ Displays past prescriptions that the GP has prescribed to the patient. """

        # reset table data
        self.ui.appointment_id_label_2.setText('appointment_id: ')
        self.ui.datetime_label_3.setText('datetime: ')
        self.ui.doctor_email_label_2.setText('doctor_email: ')
        self.ui.diagnosis_label.setText('diagnosis: ')
        self.ui.prescription_info_label.setText('prescription_info: ')
        self.ui.doctors_comment_label.setText('doctors_comment: ')

        # query database and populate patient prescriptions table.
        query_result = self.patient.search_prescriptions(self.patient.user_id)
        table_display_data(self.ui.view_prescription_table, query_result)


    def prescription_selections(self):
        """ Capture patient selection of the prescriptions table. """

        table_row_select(self.ui.view_prescription_table, 
                            [self.ui.appointment_id_label_2, self.ui.datetime_label_3, self.ui.doctor_email_label_2,
                            self.ui.diagnosis_label, self.ui.prescription_info_label, self.ui.doctors_comment_label],
                            appointment_id=0, datetime=1, doctor_email=5, diagnosis=6, prescription_info=7, doctors_comment=8)


    def patient_back(self):
        """ Controls functionality of the back button within the patient pages. """

        curr_page = self.ui.page_stackedWidget.currentIndex()

        if curr_page == 13 or curr_page == 14 or curr_page == 15:
            self.ui.page_stackedWidget.setCurrentIndex(12)
            today = datetime.datetime.now()
            formatted_today = QDate(today.year, today.month, today.day)
            self.ui.appointment_date.setSelectedDate(formatted_today)  # clear the date selection to set to current date
            self.ui.patient_back_button.hide()


    def Logout(self):
        """ Logs out the Patient, returning the user to the main login page. """

        # hide UI elements.
        self.ui.logout_pushButton.hide()
        self.ui.back_page_pushButton.hide()
        self.ui.patient_back_button.hide()
        table_goes_blank(self.ui.availabilityTable)
        table_goes_blank(self.ui.check_appointment_widget)
        self.ui.problemDescription.setPlainText('')

        # go back to login page.
        self.ui.page_stackedWidget.setCurrentIndex(0)
