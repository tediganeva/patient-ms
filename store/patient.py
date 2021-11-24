from store.user import User


class Patient(User):
    """ The Patient class groups methods required for the functionality of an Patient user. """

    def __init__(self, User):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit state and methods from the User class.
        User().__init__()


    def check_appointments(self, patient_id, current_time, view_filter):
        """ Retrieves GP requested appointments.

        Args:
            patient_id (string): the user id of the patient
            view_filter (string): additional information to provide filtering of either past or new appointments.

        Returns:
            result (list): resultset of executing an SQL query to be tabulated.
        """

        past_appointments_statment = """
            SELECT appointment_id, appointment_status_name, datetime, email, doctor_id, location, address, first_name, last_name 
            FROM appointment, availability, user, appointment_status
            WHERE appointment.patient_id = '{}'
            AND datetime < '{}'
            AND appointment.appointment_status_id = appointment_status.appointment_status_id
            AND appointment.availability_id = availability.availability_id
            AND availability.doctor_id = user.user_id
            ORDER BY datetime DESC """.format(patient_id, current_time)

        new_appointments_statement = """
            SELECT appointment_id, appointment_status_name, datetime, email, doctor_id, location, address, first_name, last_name 
            FROM appointment, availability, user, appointment_status
            WHERE appointment.patient_id = '{}'
            AND datetime > '{}'
            AND appointment.appointment_status_id = appointment_status.appointment_status_id
            AND appointment.availability_id = availability.availability_id
            AND availability.doctor_id = user.user_id
            ORDER BY datetime ASC """.format(patient_id, current_time)

        # if the patient selects the past view filter, return the resultset of the first query.
        if view_filter == 'past': 
            return self.cursor.execute(past_appointments_statment)
        
        # otherwise return the resultset of the second query to show upcoming appointments.
        else:
            return self.cursor.execute(new_appointments_statement)


    def search_gp_availability(self, datetime, location):
        """ Searches GP availabilities using date and location.

        Args:
            datetime (string): the potential date of an available GP appointment.
            location (string): the location of the general practice.

        Returns:
            result (list): resultset of executing an SQL query to be tabulated.
        """

        statement = """
            SELECT availability_id, doctor_id, datetime, address, first_name, last_name 
            FROM availability, user 
            WHERE date(datetime) = '{}'
            AND location = '{}'
            AND availability_status_id = 0
            AND user_role_id = 1 
            AND availability.doctor_id = user.user_id """.format(datetime, location)

        # return the result of the query execution to the caller
        return self.cursor.execute(statement)


    def search_prescriptions(self, patient_id):
        """ Searches prescriptions that have been prescribed to the patient.

        Args:
            patient_id (int): the user id of the patient

        Returns:
            result (list): resultset of executing an SQL query to be tabulated.
        """

        statement = """
            SELECT medical_record.appointment_id, datetime, doctor_id, first_name, last_name, email, diagnosis, prescription_info, doctors_comment
            FROM appointment, availability, medical_record, user
            WHERE (appointment.appointment_status_id =2 OR appointment.appointment_status_id =3)
            AND appointment.patient_id = '{}'
            AND availability.doctor_id = user.user_id 
            AND medical_record.appointment_id = appointment.appointment_id
            AND appointment.availability_id = availability.availability_id
            ORDER BY datetime DESC """.format(patient_id)

        # return the result of the query execution to the caller
        return self.cursor.execute(statement)


    def submit_appointment_booking(self, availability_id, patient_id, problem_info):
        """ Submits an appointment request into the database.

        This function enables the patient to submit an appointment request into the system. The patient
        selects a general practice along with the specific doctor that they want to see based on the 
        doctors availability. This then sends the request to the doctor for them later to cancel or
        confirm the appointment at their discretion.

        Args:
            availability_id (int): the unique availability_id for the doctor that the patient selected.
            patient_id (int): the user id of the patient
            problem_info (string): a summary of whats wrong with the patient.
        """

        insert_appointment_request_statement = """
            INSERT into appointment (availability_id, appointment_status_id, patient_id, patient_summary)
            VALUES('{}', '{}', '{}', '{}')""".format(availability_id, 0, patient_id, problem_info)

        update_availability_statement = """
            UPDATE availability 
            SET availability_status_id = 1 
            WHERE availability_id = '{}'""".format(availability_id)

        # execute the statements and commit it to the datebase.
        self.cursor.execute(insert_appointment_request_statement)
        self.cursor.execute(update_availability_statement)
        self.conn.commit()


    def cancel_appointment(self, appointment_id, datetime, doctor_id):
        """ Updates the appointment status of a previously booked upcoming appointment to cancelled.

        This function enables the patient to canel an appointment that they have booked. The GP will
        be able to check and confirm from their end that the appointment was cancelled by the patient.

        Args:
            appointment_id (int): the unique appointment id of the booking.
            datetime (string): the date of the appointment to be cancelled.
            doctor_id (int): the id of the GP that was to see the patient prior to cancellation.
        """

        update_appointment_statement = """
            UPDATE appointment 
            SET appointment_status_id = -2 
            WHERE appointment_id = '{}'""".format(appointment_id)

        update_availability_statement = """
            UPDATE availability 
            SET availability_status_id = 0 
            WHERE datetime = '{}' 
            AND doctor_id = '{}'""".format(datetime, doctor_id)

        # execute the statements and commit it to the datebase.
        self.cursor.execute(update_appointment_statement)
        self.cursor.execute(update_availability_statement)
        self.conn.commit()
