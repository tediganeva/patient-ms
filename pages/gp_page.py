# UI library imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# import helper widgets for UI tables.
from widgets.table_widgets import table_data_settings, table_row_select, table_display_data

# ad-hoc requirements.
import datetime
import calendar
import time

# import the GP.
from store.gp import GP

# import app.
from ehealthApp import *


class GPPages(QMainWindow):
    """ GPPages houses the view and functionality of a GP after they log in. 

    Attributes:
        GP (class): an GP object class that contains methods for a GP to query the database.
        ui (list): a list of UI components that update the visual state of the application.
    """

    def __init__(self, GP, ui):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit from QMainWindow library.
        super().__init__()

        # set the internal state variable of gp to GP class. 
        # NOTE: must not use "user" because it will be an ambigous method call and will not work.
        self.gp = GP

        # assign the ui component as an internal variable to get access to visual update features.
        self.ui = ui

        # visual update and reset internal data
        self.ui.GPname_label.setText("Hi, DR " + str(self.gp.last_name))
        self.ui.GPemail_label.setText("Email: " + str(self.gp.email))
        self.ui.logout_pushButton.show()
        self.ui.back_page_pushButton.hide()
        self.ui.GP_back_button.hide()
        self.ui.Confirm_button.button(QDialogButtonBox.Ok).setText("Confirm")
        self.ui.Confirm_button.button(QDialogButtonBox.Cancel).setText("Cancel")
        self.ui.input_name.clear()
        self.ui.input_patient_id.clear()
        self.ui.pending_table.clearSelection()
        self.ui.result_table.clearSelection()
        self.ui.view_record_button.hide()

        # clear the date selection to set to the next day
        next_day = datetime.datetime.now() + datetime.timedelta(days = 1)
        formatted_date_availability = QDate(next_day.year, next_day.month, next_day.day)
        self.ui.calendarWidget.setSelectedDate(formatted_date_availability)  

        # clear the date selection to set to to the current day
        today = datetime.datetime.now()
        formatted_date_appointment = QDate(today.year, today.month, today.day)
        self.ui.appointment_calendar.setSelectedDate(formatted_date_appointment)  

        #self.ui.calendarWidget.setSelectedDate(formatted_date)  # clear the date selection to set to the next day
        #self.ui.appointment_calendar.setSelectedDate(formatted_date)  # clear the date selection to set to to the next day

        # redirect to the correct page
        self.ui.page_stackedWidget.setCurrentIndex(6)
        self.ui.GP_back_button.clicked.connect(self.gp_back)
        self.ui.appointment_date_label.setText("datetime: ")
        self.ui.diagnosis_label_2.setText("diagnosis: ")
        self.ui.prescription_info_label_2.setText("prescription_info: ")
        self.ui.doctors_comment_label_2.setText("doctors_comment: ")

        # set up the manage availability page
        self.ui.AvailabilityPushButton.clicked.connect(self.display_availability)
        self.checkboxes = [self.ui.eight30, self.ui.eight45, self.ui.nine00, self.ui.nine15, self.ui.nine30, self.ui.nine45, self.ui.ten00,
                           self.ui.ten15, self.ui.ten30, self.ui.ten45, self.ui.eleven00, self.ui.eleven15, self.ui.eleven30, self.ui.eleven45,
                           self.ui.twelve00, self.ui.twelve15, self.ui.twelve30, self.ui.twelve45, self.ui.one00, self.ui.one15, self.ui.one30,
                           self.ui.one45, self.ui.two00, self.ui.two15, self.ui.two30, self.ui.two45, self.ui.three00, self.ui.three15, self.ui.three30,
                           self.ui.three45, self.ui.four00, self.ui.four15, self.ui.four30, self.ui.four45, self.ui.five00, self.ui.five15]

        # set up the availability calendar to enable dates between 1-30 days in advanced to be selected
        date_tomorrow = datetime.date.today() + datetime.timedelta(days = 1)
        self.ui.calendarWidget.setMinimumDate(QDate(date_tomorrow.year, date_tomorrow.month, date_tomorrow.day))
        next_month = datetime.date.today() + datetime.timedelta(days = 30)
        self.ui.calendarWidget.setMaximumDate(QDate(next_month.year, next_month.month, next_month.day))
        self.ui.calendarWidget.clicked.connect(self.display_availability)

        # set up the manage appointment page
        self.ui.missed_button.hide()
        self.ui.record_button.hide()
        self.ui.update_record_button.hide()
        self.ui.Confirm_button.hide()
        self.ui.Confirm_button.button(QDialogButtonBox.Ok).clicked.connect(self.update_appointment_signal)
        self.ui.Confirm_button.button(QDialogButtonBox.Cancel).clicked.connect(self.update_appointment_signal)
        self.ui.missed_button.clicked.connect(self.update_appointment_signal)

        # connect the button clicks in the manage appointment page to different class methods
        self.ui.AppointmentPushButton.clicked.connect(self.display_appointment)
        self.ui.appointment_calendar.clicked.connect(self.display_appointment)
        self.ui.pending_table.itemPressed.connect(self.retrieve_appointment_data_pending)
        self.ui.scheduled_table.itemPressed.connect(self.retrieve_appointment_data_scheduled)
        self.ui.update_record_button.clicked.connect(self.prescription_patient_record)
        self.ui.logout_pushButton.clicked.connect(self.Logout)
        self.ui.medical_history_table.clicked.connect(self.medical_history_selections)

        # setting up the tables
        table_data_settings(self.ui.pending_table)
        table_data_settings(self.ui.scheduled_table)
        table_data_settings(self.ui.result_table)

        # set up the manage patient page
        # connect the button clicks in the manage patient page to different class methods
        self.ui.ManagePatientPushButton.clicked.connect(self.display_manage_patient)
        self.ui.search_name_button.clicked.connect(self.display_manage_patient)
        self.ui.search_id_button.clicked.connect(self.display_manage_patient)
        self.ui.result_table.clicked.connect(self.transfer_result_data)

        # set up the issue prescriptions page
        # connect the button clicks in the issue prescription page to different class methods
        self.ui.submit_button.clicked.connect(self.issue_prescription)


    def gp_back(self):
        """ Directs to the correct page when the back button is pressed"""

        curr_page = self.ui.page_stackedWidget.currentIndex()

        if curr_page == 7 or curr_page == 8 or curr_page == 11:
            self.ui.page_stackedWidget.setCurrentIndex(6)

            # clear variables when user presses back
            self.ui.input_name.clear()
            self.ui.input_patient_id.clear()
            next_day = datetime.datetime.now() + datetime.timedelta(days = 1)
            formatted_date_availability = QDate(next_day.year, next_day.month, next_day.day)
            self.ui.calendarWidget.setSelectedDate(formatted_date_availability)  # clear the date selection to set to the next day
            today = datetime.datetime.now()
            formatted_date_appointment = QDate(today.year, today.month, today.day)
            self.ui.appointment_calendar.setSelectedDate(formatted_date_appointment)  # clear the date selection to set to to the current day
            self.ui.record_button.hide()
            self.ui.scheduled_table.clearSelection()
            self.ui.pending_table.clearSelection()
            self.ui.view_record_button.hide()
            self.ui.Confirm_button.hide()
            self.ui.GP_back_button.hide()
        elif curr_page == 10:
            self.ui.input_diagnosis.clear()
            self.ui.input_prescription.clear()
            self.ui.input_comment.clear()
            self.ui.page_stackedWidget.setCurrentIndex(8)
            self.ui.record_button.hide()
            self.ui.update_record_button.hide()
            self.ui.missed_button.hide()
            self.ui.scheduled_table.clearSelection()
            self.ui.pending_table.clearSelection()
            self.ui.GP_back_button.show()

    def display_availability(self):
        """ Displays the GP's availability with different time slots for individual days selected on the calendar."""

        self.ui.GP_back_button.show()
        self.ui.page_stackedWidget.setCurrentIndex(7)  # redirect to the correct page
        selected_date = self.ui.calendarWidget.selectedDate()  # retrieve date from the calendar widget
        availability_date = "{:4d}-{:02d}-{:02d}".format(selected_date.year(), selected_date.month(), selected_date.day())  # format the selected data to match the database date format

        for checkbox in self.checkboxes:
            # Loop over the time slot checkboxes and set it all to unchecked
            checkbox.setChecked(False)

        # For the selected date, retrieve the times already made available by the gp in the availability table
        # and check the the time slots that the gp is available
        query_result = self.gp.availability_data(self.gp.user_id, availability_date)

        availability_data = query_result.fetchall()

        for checkbox in self.checkboxes:
            for i in availability_data:
                if i[1] == (checkbox.text()[:5] + ":00"):
                    checkbox.setChecked(True)

        # connect to function with parameters when buttons on the page are clicked
        self.ui.buttonGroup.buttonClicked.connect(self.update_gp_availability_single)
        self.ui.selectAllButton.clicked.connect(self.update_gp_availability_all)
        self.ui.deselectAllButton.clicked.connect(self.update_gp_availability_all)


    def update_gp_availability_all(self):
        """ Updates the GP availability based on checkbox option selected for the entire day. """

        # retrieve date from the calendar widget
        selected_date = self.ui.calendarWidget.selectedDate()
        availability_date = "{:4d}-{:02d}-{:02d}".format(selected_date.year(), selected_date.month(), selected_date.day())  # format the selected data to match the database date format
        action=self.sender()
        # add entire day as the GP's availability.
        if action.text() == "Select All":
            for checkbox in self.checkboxes:
                checkbox.setChecked(True)
                time = checkbox.text()
                availabile_time = availability_date + " " + time[0:5]

                # update gp availability for the whole day
                self.gp.update_availability_add(self.gp.user_id, availabile_time)

        # remove the GP's availability for the entire day.
        if action.text() == "Deselect All":
            for checkbox in self.checkboxes:
                checkbox.setChecked(False)
                time = checkbox.text()
                availabile_time = availability_date + " " + time[0:5]

                # remove gp availability for the entire day.
                self.gp.update_availability_remove(self.gp.user_id, availabile_time)


    def update_gp_availability_single(self):
        """ Updates the GP availability based on checkbox option selected for individual checkboxes. """

        # retrieve date from the calendar widget
        selected_date = self.ui.calendarWidget.selectedDate()
        availability_date = "{:4d}-{:02d}-{:02d}".format(selected_date.year(), selected_date.month(),selected_date.day())  # format the selected data to match the database date format
        # update GP selected dates and times for their availability.
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                time = checkbox.text()
                availabile_time = availability_date + " " + time[0:5]

                # update gp availability for the specified datetime.
                self.gp.update_availability_add(self.gp.user_id, availabile_time)

            else:
                time = checkbox.text()
                availabile_time = availability_date + " " + time[0:5]

                # remove gp for unspecified datetime.
                self.gp.update_availability_remove(self.gp.user_id, availabile_time)


    def display_appointment(self):
        """ Display the appointments requested to the GP in a pending table and all appointments confirmed in a scheduled table."""

        # set up the manage appointment page
        self.ui.patient_record_back_button.hide()
        self.ui.GP_back_button.show()
        self.ui.page_stackedWidget.setCurrentIndex(8)  # redirect to the correct page
        selected_date = self.ui.appointment_calendar.selectedDate()  # retrieve date from the calendar widget
        appointment_date = "{:4d}-{:02d}-{:02d}".format(selected_date.year(), selected_date.month(), selected_date.day())
        today = datetime.datetime.today().strftime('%Y-%m-%d')  #formated current date

        # display appointment data for the appointment requested by patient table that are 1 day in advance of the current date.
        pending_appointments_query_result = self.gp.display_pending_appointments(self.gp.user_id, today)
        table_display_data(self.ui.pending_table, pending_appointments_query_result)
        self.ui.pending_table.resizeColumnsToContents()

        # display appointment data for the scheduled appointment table
        # only appointment with appointment status = confirmed or completed with prescription or or completed without prescription are displayed
        confirmed_appointments_query_result = self.gp.display_confirmed_appointments(self.gp.user_id, appointment_date)
        table_display_data(self.ui.scheduled_table, confirmed_appointments_query_result)
        self.ui.scheduled_table.resizeColumnsToContents()

        # hide the buttons:
        self.ui.record_button.hide()
        self.ui.update_record_button.hide()
        self.ui.missed_button.hide()
        self.ui.Confirm_button.hide()


    def retrieve_appointment_data_pending(self):
        """ Retrieve the appointment data of the selected row in the pending appointment table
            Based the status of the appointment, varies options for the appointment is displayed

        Return:
            the appointment_id and the appointment datatime of the selected appointment from the pending appointment table
        """
        self.ui.Confirm_button.hide()
        self.ui.record_button.hide()
        self.ui.update_record_button.hide()
        self.ui.missed_button.hide()

        self.ui.scheduled_table.clearSelection()
        self.ui.record_button.hide()
        self.ui.update_record_button.hide()
        self.ui.missed_button.hide()
        selected_date = self.ui.appointment_calendar.selectedDate()
        index = self.ui.pending_table.selectionModel().currentIndex()  #retrieve the index of the selected data
        appointment_id = index.sibling(index.row(), 0).data() #retrieve the appointment id of the selected appointment using the index
        pending_appointment_datetime=index.sibling(index.row(), 4).data()
        if index is not None:
            # when a row is selected, give the option to confirm or remove the appointment by presenting the confirm and remove button
            self.ui.Confirm_button.show()
        else:
            self.ui.Confirm_button.hide()
        return appointment_id,pending_appointment_datetime

    def retrieve_appointment_data_scheduled(self):
        """ Retrieve the appointment data of the selected row in the scheduled appointment table
            Based the status of the appointment, varies options for the appointment is displayed

        Return:
            the appointment_id and the patient_id of the selected appointment from the scheduled appointment table
        """
        self.ui.pending_table.clearSelection()
        self.ui.Confirm_button.hide()

        try:
            index = self.ui.scheduled_table.selectionModel().currentIndex()  #retrieve the index of the selected data
            appointment_id = index.sibling(index.row(), 0).data()#retrieve the appointment id of the selected appointment using the index
            patient_id = index.sibling(index.row(), 1).data()#retrieve the patient_id of the selected appointment using the index
            selected_date = self.ui.appointment_calendar.selectedDate()  # retrieve date from the calendar widget
            appointment_date = "{:4d}-{:02d}-{:02d}".format(selected_date.year(), selected_date.month(), selected_date.day())
            appointment_time=index.sibling(index.row(), 4).data()
            appointment_datetime = time.strptime((appointment_date + " " + appointment_time), "%Y-%m-%d %H:%M:%S")
            appointment_datetime_formatted = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds = calendar.timegm(appointment_datetime))

            # Display the different options available for the selected appointment depending on the date and appointment status selected
            if appointment_datetime_formatted > datetime.datetime.now():
                # for appointment times that have not exceeded the current time, only allow the GP to view medical record
                self.ui.record_button.show()
                self.ui.update_record_button.hide()
                self.ui.missed_button.hide()

            else:
                # for past dates, give the GP option to view and update medical record and update the appointment status if patient missed the appointment
                if index.sibling(index.row(), 5).data() == "CONFIRMED":
                    # When a row is selected, give the option change the status of the appointment to missed by patient and update it in the database
                    self.ui.missed_button.hide()
                    self.ui.record_button.show()
                    self.ui.update_record_button.hide()

                elif index.sibling(index.row(), 5).data() == "GP ACTION REQUIRED":
                    self.ui.missed_button.show()
                    self.ui.record_button.show()
                    self.ui.update_record_button.show()

                elif index.sibling(index.row(), 5).data() == "MISSED BY PATIENT":
                    self.ui.missed_button.hide()
                    self.ui.record_button.show()
                    self.ui.update_record_button.hide()

                else:
                    # If the appointment status is completed (with or without prescription), GP cannot change status of appointment to missed by patient
                    # GP can still view and update medical record
                    self.ui.missed_button.hide()
                    self.ui.record_button.show()
                    self.ui.update_record_button.show()

            # connect to view the patient's record from the manage appointment page when the view record button is clicked
            # the patient id for the patient's medical record data is passed
            self.ui.record_button.clicked.connect(self.patient_record)
            return appointment_id,patient_id

        except TypeError:
            self.display_appointment()


    def update_appointment_signal(self):
        """ Receives the signal from the signal from the update appointment status buttons and
        pass these with the appointment id to the database.
        """
        sender = self.sender()
        if sender.text() == "Confirm":
            appointment_id, appointment_datetime = self.retrieve_appointment_data_pending()
            self.gp.update_appointment(appointment_id, self.gp.user_id, appointment_datetime, "confirm")
            self.ui.Confirm_button.hide()

        elif sender.text() == "Cancel":
            appointment_id, appointment_datetime = self.retrieve_appointment_data_pending()
            self.gp.update_appointment(appointment_id, self.gp.user_id, appointment_datetime, "remove")
            self.ui.Confirm_button.hide()

        elif sender.text() == "Missed":
            appointment_id,patient_id = self.retrieve_appointment_data_scheduled()
            self.gp.update_appointment(appointment_id, self.gp.user_id, "", "missed")

            self.ui.missed_button.hide()
            self.ui.record_button.hide()
            self.ui.update_record_button.hide()

        # navigate to the display appointment page after update.
        self.display_appointment()


    def patient_record(self):
        """ Receive patient data from the data with the patient ID and display it in the medical record page"""

        # page setup to direct to the correct page and show the current widgets in the page
        self.ui.page_stackedWidget.setCurrentIndex(9)  # redirect to the patient record page
        #set up the back buttons so when it's pressed, it will return to the correct page that it was directed from.
        self.ui.patient_record_back_button.show()
        self.ui.GP_back_button.hide()
        self.ui.missed_button.hide()
        self.ui.record_button.hide()
        self.ui.update_record_button.hide()
        page=self.sender()
        if page.text() == "Medical Record":
            self.ui.patient_record_back_button.clicked.connect(self.display_appointment)  # returns to the manage appointment page
            # retrieve the patient's data from the the scheduled appointment table
            appointment_id, patient_id = self.retrieve_appointment_data_scheduled()
        elif page.text() == "View Medical Record":
            self.ui.patient_record_back_button.clicked.connect(self.display_manage_patient)   # returns to the manage patient page
            # retrieve the patient's data from the the result table from the manage patient page
            patient_id = self.transfer_result_data()
            print(patient_id)

        # retrieve the patient's personal data from the database using data from the scheduled table
        personal_data = self.gp.patient_data(patient_id, "patient", "personal")

        # display the patient's personal information to the gp when a patient is selected, if no patient was selected,
        # no data would be returned, index error would raise, when this error occurs, return to the appointment page.
        try:
            self.ui.patient_information_list.clear()
            self.ui.patient_information_list.addItem("Patient ID: " + str(personal_data[0][0]))
            self.ui.patient_information_list.addItem("First Name: " + str(personal_data[0][1]))
            self.ui.patient_information_list.addItem("Last Name: " + str(personal_data[0][2]))
            self.ui.patient_information_list.addItem("Email: " + str(personal_data[0][3]))
            self.ui.patient_information_list.addItem("Phone Number: " + str(personal_data[0][4]))
            self.ui.patient_information_list.addItem("Location: " + str(personal_data[0][5]))
            self.ui.patient_information_list.addItem("Address: " + str(personal_data[0][6]))

        except IndexError:
            # if no data as selected in the table and the view medical record button is pressed
            # return to the same page
            if page == "manage_appointment":
                self.ui.page_stackedWidget.setCurrentIndex(8)

            if page == "manage_patient":
                self.ui.page_stackedWidget.setCurrentIndex(11)
        
        # Reset table data
        self.ui.appointment_date_label.setText("datetime: ")
        self.ui.diagnosis_label_2.setText("diagnosis: ")
        self.ui.prescription_info_label_2.setText("prescription_info: ")
        self.ui.doctors_comment_label_2.setText("doctors_comment: ")

        # Retrieve the patient's medical record from the database using the patient's id and display it in a table.
        medical_record_query_result = self.gp.patient_data(patient_id, "patient", "medical")
        table_display_data(self.ui.medical_history_table, medical_record_query_result)

        self.ui.scheduled_table.clearSelection()
        self.ui.result_table.clearSelection()

    def medical_history_selections(self):
        """ Capture GP selection of the medical history table """

        table_row_select(self.ui.medical_history_table,
                            [self.ui.appointment_date_label, self.ui.diagnosis_label_2, self.ui.prescription_info_label_2,
                            self.ui.doctors_comment_label_2], datetime = 0, diagnosis = 1, prescription_info = 2, doctors_comment = 3)


    def prescription_patient_record(self):
        """ Display the patients past medical history. """

        # page set up to direct to the correct page and show the current widgets in the page
        self.ui.GP_back_button.show()
        self.ui.page_stackedWidget.setCurrentIndex(10)
        self.ui.input_prescription.clear()
        self.ui.input_diagnosis.clear()
        self.ui.input_comment.clear()
        self.ui.fields_error_label_3.hide()

        appointment_id_scheduled,patient_id = self.retrieve_appointment_data_scheduled()
        personal_data = self.gp.patient_data(appointment_id_scheduled, "appointment", "personal")

        try:
            self.ui.patient_info_list.clear()
            self.ui.patient_info_list.addItem("Patient ID: "+str(personal_data[0][0]))
            self.ui.patient_info_list.addItem("First Name: "+ str(personal_data[0][1]))
            self.ui.patient_info_list.addItem("Last Name: "+ str(personal_data[0][2]))
            self.ui.patient_info_list.addItem("Email: "+ str(personal_data[0][3]))
            self.ui.patient_info_list.addItem("Phone Number: "+str(personal_data[0][4]))
            self.ui.patient_info_list.addItem("Location: "+str(personal_data[0][5]))
            self.ui.patient_info_list.addItem("Address: "+str(personal_data[0][6]))

        except IndexError:
            self.ui.page_stackedWidget.setCurrentIndex(8)

        appointment_data = self.gp.patient_data(appointment_id_scheduled, "appointment", "appointment")

        try:
            self.ui.appointment_info_list.clear()
            self.ui.appointment_info_list.addItem("Appointment ID: " + str(appointment_data[0][0]))
            self.ui.appointment_info_list.addItem("Appointment Status: " + str(appointment_data[0][1]))
            self.ui.appointment_info_list.addItem("Appointment Time: " + str(appointment_data[0][2]))
            self.ui.appointment_info_list.addItem("Patient Summary: " + str(appointment_data[0][3]))

        except IndexError:
            self.ui.page_stackedWidget.setCurrentIndex(8)
        
        # query database and view the base prescriptions
        query = self.gp.view_past_prescriptions(appointment_id_scheduled)

        row = query.fetchall()

        if len(row) == 1:
            self.ui.input_diagnosis.setText(row[0][1])
            self.ui.input_prescription.setText(row[0][2])
            self.ui.input_comment.setText(row[0][3])

        else:
            self.ui.input_diagnosis.clear()
            self.ui.input_prescription.clear()
            self.ui.input_comment.clear()
    
    
    def issue_prescription(self):
        """ Issues a prescription to a patient that has finished an appointment. """

        appointment_id_scheduled, patient_id = self.retrieve_appointment_data_scheduled()
        prescription_description = self.ui.input_prescription.toPlainText().strip().replace('\n', ';')
        diagnosis = self.ui.input_diagnosis.toPlainText().strip().replace('\n', ';')
        comment = self.ui.input_comment.toPlainText().strip().replace('\n', ';')

        if diagnosis == "" or comment == "":
            self.ui.fields_error_label_3.setText('Please fill in diagnosis and comment!')
            self.ui.fields_error_label_3.show()

        elif len(diagnosis) > 200:
            self.ui.fields_error_label_3.setText('Diagnosis Too Long!')
            self.ui.fields_error_label_3.show()

        elif len(comment) > 200:
            self.ui.fields_error_label_3.setText('Comment Too Long!')
            self.ui.fields_error_label_3.show()

        elif len(prescription_description) > 200:
            self.ui.fields_error_label_3.setText('Prescription Too Long!')
            self.ui.fields_error_label_3.show()

        else:
            # issue the prescription to the patient.
            self.gp.issue_prescription(appointment_id_scheduled, prescription_description, diagnosis, comment)

            # call the display appointment function to go to manage appointment page; updates taken into account
            self.display_appointment()


    def display_manage_patient(self):
        """ Display the manage patient page where GP searches for patients and views their personal data in a result table
        """

        # redirects to the manage patient page
        self.ui.page_stackedWidget.setCurrentIndex(11) 
        self.ui.patient_record_back_button.hide()
        self.ui.view_record_button.hide()
        self.ui.GP_back_button.show()

        #element: either the name_button or id_button label that the GP clicked on.
        element=self.sender()
        # display all patients in the database
        if element.text() == "Manage Patient":
            query_result = self.gp.search_patients_via_name("")
            table_display_data(self.ui.result_table, query_result)

        # gp selected the name filter, search patients based on their first name and last name and get result.
        if element.text() == "Search by Name":
            self.ui.input_patient_id.clear()
            name = self.ui.input_name.text().strip()
            query_result = self.gp.search_patients_via_name(name)
            table_display_data(self.ui.result_table, query_result)

        # gp selected the id filter, search patients based on their unique user id and get result.
        if element.text() == "Search by ID":
            self.ui.input_name.clear()
            patient_id = self.ui.input_patient_id.text().strip()
            query_result = self.gp.search_patients_via_id(patient_id)
            table_display_data(self.ui.result_table, query_result)


    def transfer_result_data(self):
        """ Passes the selected patient's patient ID from the result table to the patient record page
        to view the patient's medical record
        Returns:
            the patient_id of the selected record
        """

        self.ui.view_record_button.show() # GP can only view medical record if patient is selected
        index = self.ui.result_table.selectionModel().currentIndex()
        patient_id = index.sibling(index.row(), 0).data()
        print(patient_id)
        self.ui.view_record_button.clicked.connect(self.patient_record)
        return patient_id


    def Logout(self):
        """ Logs out the GP, returning the user to the main login page. """
        # go back to login page.
        self.ui.page_stackedWidget.setCurrentIndex(0)

        self.ui.logout_pushButton.hide()
        self.ui.back_page_pushButton.hide()
        self.ui.patient_record_back_button.hide()
        self.ui.GP_back_button.hide()
        self.ui.input_diagnosis.clear()
        self.ui.input_prescription.clear()
        self.ui.input_comment.clear()
