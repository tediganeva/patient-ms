from store.user import User


class GP(User):
    """ The GP class groups methods required for the functionality of an GP user. """

    def __init__(self, User):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit state and methods from the User class.
        User().__init__()


    def availability_data(self, gp_id, availability_date):
        """ Fetch the availability slots that the gp already made available

        Args:
            gp_id (int): the GP's user id.
            availability_date: the selected date for the availability data

        Returns:
            result (list): the set of time slots that the GP is available
        """

        statement = """
            SELECT date(datetime), time(datetime) 
            FROM availability 
            WHERE doctor_id = '{}' 
            AND date(datetime) = '{}'""".format(gp_id, availability_date)

        return self.cursor.execute(statement)


    def update_availability_add(self, gp_id, timestamp):
        """ Adds entry into GP availability at specified time.

         Args:
             gp_id (int): the GP's user id.
             timestamp (string): the date + time that the GP is available.
        """

        # statement that checks whether the availability already exists in the database.
        check_availability_statement = """
            SELECT datetime 
            FROM availability 
            WHERE doctor_id = '{}' 
            AND datetime = '{}'""".format(gp_id, timestamp)

        # statement that inserts the new availability into the database.
        insert_availability_statement = """
            INSERT INTO availability (doctor_id, datetime, availability_status_id) 
            VALUES ('{}', '{}', '{}')""".format(gp_id, timestamp, 0)

        result = self.cursor.execute(check_availability_statement)
        row = result.fetchall()

        # if the date does not already exists in the database then execure the insert statement.
        if len(row) < 1:
            self.cursor.execute(insert_availability_statement)

        self.conn.commit()


    def update_availability_remove(self, gp_id, timestamp):
        """ Removes GP availability at specified time.

         Args:
             gp_id (int): the GP's user id.
             timestamp (string): the date + time that the GP is available.
        """

        statement = """
            DELETE FROM availability 
            WHERE doctor_id = '{}' 
            AND datetime = '{}'""".format(gp_id, timestamp)
        
        self.cursor.execute(statement)

        self.conn.commit()


    def display_pending_appointments(self, gp_id, appointment_date):
        """ Fetch list of appointments with a status of pending.

        Args:
            gp_id (int): the GP's user id.
            appointment_date (string): the selected date for the availability data

        Returns:
            result (list): the set of time slots that the GP is available
        """

        statement = """
            SELECT appointment_id, user_id, first_name, last_name, datetime, patient_summary 
            FROM user, appointment, availability
            WHERE user.user_id = patient_id 
            AND appointment_status_id = '0' 
            AND date(datetime) > '{}'
            AND appointment.availability_id = availability.availability_id 
            AND doctor_id = '{}'
            ORDER BY datetime ASC""".format(appointment_date, gp_id)

        return self.cursor.execute(statement)


    def display_confirmed_appointments(self, gp_id, appointment_date):
        """ Fetch list of appointments with a status of confirmed.

        Args:
            gp_id (int): the GP's user id.
            appointment_date (string): the selected date for the availability data

        Returns:
            result (list): the set of time slots that the GP is available
        """

        statement = """
            SELECT appointment_id,user_id,first_name, last_name, time(datetime), appointment_status_name, patient_summary
            FROM user, appointment, availability, appointment_status
            WHERE user.user_id = patient_id 
            AND (appointment.appointment_status_id > 0 OR appointment.appointment_status_id = -3)
            AND appointment.availability_id=availability.availability_id
            AND appointment.appointment_status_id = appointment_status.appointment_status_id
            AND date(datetime) = '{}' 
            AND doctor_id = '{}'
            ORDER BY time(datetime) ASC""".format(appointment_date, gp_id)

        return self.cursor.execute(statement)


    def update_appointment(self, appointment_id, gp_id, appointment_time, action):
        """ Update the status of the selected appointment based on the option the GP selects.

         Args:
             appointment_id (int): the unique id of the appointment.
             gp_id (int): the GP's user id.
             appointment_time (string): the time of the appointment.
             action (string): the option the gp selects (confirm, remove or missed).
        """

        confirm_appointment_statement = """
            UPDATE appointment 
            SET appointment_status_id = 1 
            WHERE appointment_id = '{}'""".format(appointment_id)

        remove_appointment_statement = """
            UPDATE appointment 
            SET appointment_status_id = -1 
            WHERE appointment_id = '{}'""".format(appointment_id)

        update_removed_appointment_availability_statement = """
            UPDATE availability 
            SET availability_status_id = 0 
            WHERE datetime = '{}'
            AND doctor_id = '{}'""".format(appointment_time, gp_id)

        missed_appointment_statement = """
            UPDATE appointment 
            SET appointment_status_id = -3 
            WHERE appointment_id = '{}'""".format(appointment_id)

        # GP approves the appointment requested by the patient
        if action == "confirm":
            self.cursor.execute(confirm_appointment_statement)

        # GP cancels the appointment requested by the patient change the appointment status to cancelled by GP
        # change the availability status of the appointment to 0 - available
        elif action == "remove":
            self.cursor.execute(remove_appointment_statement)
            self.cursor.execute (update_removed_appointment_availability_statement)

        elif action == "missed":
            # GP changes the status of the appointment when the patient misses the appointment
            self.cursor.execute(missed_appointment_statement)

        self.conn.commit()


    def patient_data(self, id, id_type, data_type):
        """ Retrieves the patient's data from the database

         Args:
             id (int): id of the appointment or the patient
             id_type (string): appointment or patient
             data_type (string): personal data,medical data or appointment data

        Returns:
            row (list): resultset row of executing an SQL query.
        """

        # Retrieve the patient's personal data using the patient id
        if data_type == "personal" and id_type == "patient":
            res = self.cursor.execute("""SELECT user_id,first_name, last_name, email, phone_num, location, address 
                                        FROM user WHERE user_id=? """, (id,))
            row = res.fetchall()
            return row

        # Retrieve the patient's personal data using the appointment id
        elif data_type == "personal" and id_type == "appointment":
            res = self.cursor.execute("""SELECT user_id,first_name, last_name, email, phone_num, location, address 
                                FROM appointment, user WHERE appointment_id=? AND appointment.patient_id=user.user_id """,
                                 (id,))
            row = res.fetchall()
            return row

        # Retrieve the patient's medical data using the patient id
        elif data_type == "medical" and id_type == "patient":
            res = self.cursor.execute("""SELECT datetime,diagnosis, prescription_info, doctors_comment
                    FROM medical_record, appointment,availability,user WHERE appointment.appointment_id=medical_record.appointment_id
                                 AND appointment.availability_id=availability.availability_id AND appointment.patient_id=user.user_id
                                 AND appointment.patient_id=?
                                 ORDER BY datetime ASC """, (id,))
            row = res.fetchall()
            return row

        # Retrieve the patient's appointment data using the appointment id
        elif data_type == "appointment" and id_type == "appointment":
            res = self.cursor.execute("""SELECT appointment_id, appointment_status_name, time(datetime), patient_summary
                                FROM appointment, availability, appointment_status 
                                WHERE appointment_id=? AND appointment.appointment_status_id=appointment_status.appointment_status_id """,
                                 (id,))
            row = res.fetchall()
            return row


    def view_past_prescriptions(self, appointment_id,):
        """ Allows a gp to view a previous prescription of an appointment.

        Args:
             appointment_id (int): the unique id of the appointment.

        Returns:
            result (list): resultset of executing an SQL query.
        """

        statement = """
            SELECT medical_record.appointment_id, diagnosis, prescription_info, doctors_comment
            FROM medical_record, appointment 
            WHERE appointment.appointment_id = '{}' 
            AND appointment.appointment_id = medical_record.appointment_id""".format(appointment_id)

        return self.cursor.execute(statement)


    def issue_prescription(self, appointment_id, prescription_info, diagnosis, doctors_comment):
        """ Issues a prescription to a patient that has finished an appointment.

        Args:
             appointment_id (int): the unique id of the appointment.
             prescription_info (string): the specific prescription information.
             diagnosis (string): the doctors diagnosis of the patients illness for records keeping.
             doctors_comment (string): any extra comments the doctor has regarding the patient.
        """
        
        # update appointment status statement executed if prescription not given.
        no_prescription_statement = """
            UPDATE appointment 
            SET appointment_status_id = 2 
            WHERE appointment_id = '{}'""".format(appointment_id)

        # update appointment status statement executed if prescription was given at appointment.
        prescription_given_statement = """
            UPDATE appointment 
            SET appointment_status_id = 3 
            WHERE appointment_id = '{}'""".format(appointment_id)
        # statement to check if a medical record already exists in the database.

        check_record_exists_statement = """
            SELECT appointment_id, prescription_info, diagnosis, doctors_comment 
            FROM medical_record
            WHERE appointment_id = '{}'""".format(appointment_id)

        insert_new_record_statement = """
            INSERT INTO medical_record (appointment_id, prescription_info, diagnosis, doctors_comment) 
            VALUES ('{}','{}','{}','{}')""".format(appointment_id, prescription_info, diagnosis, doctors_comment)

        update_record_statement = """
            UPDATE medical_record 
            SET prescription_info = '{}', diagnosis = '{}', doctors_comment = '{}' 
            WHERE appointment_id = '{}'""".format(prescription_info, diagnosis, doctors_comment, appointment_id)

        if prescription_info == "":
            self.cursor.execute(no_prescription_statement)

        else:
            self.cursor.execute(prescription_given_statement)

        self.conn.commit()

        result = self.cursor.execute(check_record_exists_statement)

        row = result.fetchone()

        # if no rows are return from above query then this is a new appointment record.
        if row is None:
            self.cursor.execute(insert_new_record_statement)

        # an existing appointment record is being updated.
        else:
            self.cursor.execute(update_record_statement)

        self.conn.commit()


    def search_patients_via_name(self, patient_name):
        """ Search the database for patients using their full name.

        Args:
             patient_name (string): the name of the patient.

        Returns:
            result (list): resultset of executing an SQL query.
        """
        
        # prepares the patient name to be searched using the 'LIKE' function of SQL.
        sql_prepared_name = "%" + patient_name + "%"

        statement = """
            SELECT user_id, first_name, last_name, phone_num,address, location
            FROM user 
            WHERE (first_name LIKE '{}' OR last_name LIKE '{}') 
            AND user_role_id = 2 
            AND user_status_id = 1""".format(sql_prepared_name, sql_prepared_name)

        # default search if the patient_name is empty.
        empty_name_statement = """
            SELECT user_id, first_name, last_name, phone_num,address, location
            FROM user 
            WHERE user_role_id = 2 
            AND user_status_id = 1"""

        if patient_name == "":
            return self.cursor.execute(empty_name_statement)
        
        else:
            return self.cursor.execute(statement)


    def search_patients_via_id(self, patient_id):
        """ Search the database for patients using their user id.

        Args:
             patient_id (int): the user id of the patient.

        Returns:
            result (list): resultset of executing an SQL query.
        """

        statement = """
            SELECT user_id, first_name, last_name, phone_num,address, location
            FROM user 
            WHERE user_id = '{}' 
            AND user_role_id = 2
            AND user_status_id = 1""".format(patient_id)

        # default search if the patient_id is empty.
        empty_id_statement = """
            SELECT user_id, first_name, last_name, phone_num,address, location
            FROM user 
            WHERE user_role_id = 2 
            AND user_status_id = 1"""

        if patient_id == "":
            return self.cursor.execute(empty_id_statement)
        
        else:
            return self.cursor.execute(statement)
