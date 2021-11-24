import os
import unittest

import store
from store.conn import connect_to_database
from store.register import Register
from store.storage import Storage
from store.user import User

""" Unit test helper methods """


def fetch_user_status(cursor, user_id):
    cursor.execute("SELECT user_status_id FROM user WHERE user_id= '{}'".format(user_id))
    return cursor.fetchall()


def fetch_user(cursor, user_id):
    cursor.execute("SELECT * FROM user WHERE user_id= '{}'".format(user_id))
    return cursor.fetchall()


def fetch_user_status_table(cursor):
    cursor.execute("SELECT * FROM user_status")
    return cursor.fetchall()


def fetch_user_role_table(cursor):
    cursor.execute("SELECT * FROM user_role")
    return cursor.fetchall()


def fetch_availability_status_table(cursor):
    cursor.execute("SELECT * FROM availability_status")
    return cursor.fetchall()


def fetch_appointment_status_table(cursor):
    cursor.execute("SELECT * FROM appointment_status")
    return cursor.fetchall()


class TestStorageFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists("./store/UCLH.db"):
            from store.conn import create_database
            create_database()

    def test_establish_connection(self):
        s = Storage()
        self.assertIsNone(s.conn)
        self.assertIsNone(s.cursor)
        s._establish_connection()
        # Check validity of connection and cursor
        self.assertIsNotNone(s.conn)
        self.assertIsNotNone(s.cursor)


""" Unit tests """


class TestDatabaseCreation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists("./store/UCLH.db"):
            from store.conn import create_database
            create_database()
        cls.conn, cls.cursor = connect_to_database()

    def test_validate_user_status(self):
        required = [(-1, 'DEACTIVATED'), (0, 'PENDING ACTIVATION'), (1, 'ACTIVATED')]
        self.assertEqual(fetch_user_status_table(self.cursor), required)

    def test_validate_user_role(self):
        required = [(0, 'ADMIN'), (1, 'GP'), (2, 'PATIENT')]
        self.assertEqual(fetch_user_role_table(self.cursor), required)

    def test_validate_avalability_status_table(self):
        required = [(0, 'AVAILABLE'), (1, 'UNAVAILABLE')]
        self.assertEqual(fetch_availability_status_table(self.cursor), required)

    def test_validate_appointment_status_table(self):
        required = [
            (-4, 'CANCELLED BY SYSTEM'),
            (-3, 'MISSED BY PATIENT'),
            (-2, 'CANCELLED BY PATIENT'),
            (-1, 'CANCELLED BY GP'),
            (0, 'PENDING CONFIRMATION'),
            (1, 'CONFIRMED'),
            (2, 'COMPLETED WITHOUT PRESCRIPTION'),
            (3, 'COMPLETED WITH PRESCRIPTION'),
            (4, 'GP ACTION REQUIRED'),
        ]
        self.assertEqual(fetch_appointment_status_table(self.cursor), required)


""" Unit tests. """


class TestAdminFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists("./store/UCLH.db"):
            from store.conn import create_database
            create_database()

    @classmethod
    def tearDownClass(cls):
        from store.conn import create_database, connect_to_database
        create_database()
        conn, cursor = connect_to_database()
        cursor.execute("UPDATE user SET user_id=2 WHERE email='gp@mail.com'")
        cursor.execute("UPDATE user SET user_id=3 WHERE email='patient@mail.com'")
        conn.commit()
        conn.close()

    def test_admin_login(self):
        """ Loggin in with Admin credentials should create an Admin Class. """

        stranger = User.create_user()
        admin = stranger.login(stranger, "admin@mail.com", "AdminPassword")

        # check that stranger who was a User class has changed to an instance of the Admin class.
        self.assertIsInstance(admin, store.admin.Admin)

        # check that the user_id is 1 (first user in database).
        self.assertIs(admin.user_id, 1)

        # test and check that the user_role is 0 (Admin).
        self.assertIs(admin.user_role_id, 0)

        # print(help(admin)) # uncomment below for extra information 🔎

    def test_deactivate_user(self):
        """ Test deactivating user, function should handle invalid parameters."""

        stranger = User.create_user()
        admin = stranger.login(stranger, "admin@mail.com", "AdminPassword")
        # Deactive an initialized GP
        admin.deactivate_user(2)
        # Deactive an initialized patient
        admin.deactivate_user(3)
        self.assertEqual(fetch_user_status(admin.cursor, 2), [(-1,)])
        self.assertEqual(fetch_user_status(admin.cursor, 3), [(-1,)])

    def test_activate_user(self):
        """ Test activating user, function should handle invalid parameters."""

        stranger = User.create_user()
        admin = stranger.login(stranger, "admin@mail.com", "AdminPassword")
        # Active an initialized GP
        admin.activate_user(2)
        # Active an initialized patient
        admin.activate_user(3)
        self.assertEqual(fetch_user_status(admin.cursor, 2), [(1,)])
        self.assertEqual(fetch_user_status(admin.cursor, 3), [(1,)])

    def test_delete_user(self):
        """ Test deleting user, function should handle invalid parameters."""

        stranger = User.create_user()
        admin = stranger.login(stranger, "admin@mail.com", "AdminPassword")
        # Delete an initialized GP
        admin.delete_user("2")
        # Delete an initialized patient
        self.assertEqual(fetch_user(admin.cursor, "2"), [])
        # Test double deleting
        self.assertFalse(admin.delete_user("3"))
        self.assertFalse(admin.delete_user("3"))


class TestGPFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from store.conn import create_database, connect_to_database
        if not os.path.exists("./store/UCLH.db"):
            create_database()
        conn, cursor = connect_to_database()
        cursor.execute(
            "INSERT OR IGNORE INTO availability (availability_id,doctor_id,datetime,availability_status_id) VALUES (16384,2,'2020-01-30',0)")
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        from store.conn import connect_to_database
        conn, cursor = connect_to_database()
        cursor.execute(
            "DELETE FROM availability WHERE availability_id='16384'")
        conn.commit()
        conn.close()

    def test_update_appointment(self):
        def helper(cursor, id):
            cursor.execute("SELECT * FROM appointment WHERE appointment_id= '{}'".format(id))
            return cursor.fetchall()

        stranger = User.create_user()
        gp = stranger.login(stranger, "gp@mail.com", "GpPassword")
        gp.cursor.execute(
            "INSERT OR IGNORE INTO appointment (appointment_id,availability_id,appointment_status_id,patient_id,patient_summary) VALUES (16384,16384,0,1,'TESTSUMMARY')")
        gp.conn.commit()
        gp.update_appointment(16384, 2, "2020-01-30", "confirm")
        self.assertEqual(helper(gp.cursor, 16384), [(16384, 16384, 1, 1, 'TESTSUMMARY',)])
        gp.update_appointment(16384, 2, "2020-01-30", "remove")
        self.assertEqual(helper(gp.cursor, 16384), [(16384, 16384, -1, 1, 'TESTSUMMARY',)])
        gp.update_appointment(16384, 2, "2020-01-30", "confirm")
        gp.update_appointment(16384, 2, "2020-01-30", "missed")
        self.assertEqual(helper(gp.cursor, 16384), [(16384, 16384, -3, 1, 'TESTSUMMARY',)])
        gp.cursor.execute(
            "DELETE FROM appointment WHERE appointment_id=16384")
        gp.conn.commit()


""" Helper method"""


def helper_appointment(cursor, id):
    cursor.execute("SELECT * FROM appointment WHERE appointment_id= '{}'".format(id))
    return cursor.fetchall()


def helper_avalibility(cursor, id):
    cursor.execute("SELECT * FROM availability WHERE availability_id = '{}'".format(id))
    return cursor.fetchall()


class TestPatientFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        from store.conn import create_database, connect_to_database
        if not os.path.exists("./store/UCLH.db"):
            create_database()
        conn, cursor = connect_to_database()
        cursor.execute(
            "INSERT OR IGNORE INTO availability (availability_id,doctor_id,datetime,availability_status_id) VALUES (16384,2,'2020-01-30',0)")
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(self):
        from store.conn import connect_to_database
        conn, cursor = connect_to_database()
        cursor.execute(
            "DELETE FROM availability WHERE availability_id='16384'")
        conn.close()

    def test_submit_appointment(self):
        stranger = User.create_user()
        patient = stranger.login(stranger, "patient@mail.com", "PatientPassword")
        patient.submit_appointment_booking(16384, patient.user_id, "TEST")
        conn, cursor = connect_to_database()
        cursor.execute("SELECT appointment_id FROM appointment WHERE availability_id=16384 AND patient_summary='TEST'")
        id = cursor.fetchone()
        self.assertEqual(helper_appointment(patient.cursor, id[0]), [(id[0], 16384, 0, patient.user_id, 'TEST',)])
        self.assertEqual(helper_avalibility(patient.cursor, 16384), [(16384, 2, '2020-01-30', 1)])
        cursor.execute("DELETE FROM appointment WHERE availability_id=16384 AND patient_summary='TEST'")
        conn.commit()

    def test_cancel_appointment(self):
        stranger = User.create_user()
        patient = stranger.login(stranger, "patient@mail.com", "PatientPassword")
        patient.submit_appointment_booking(16384, patient.user_id, "TEST")
        conn, cursor = connect_to_database()
        cursor.execute("SELECT appointment_id FROM appointment WHERE availability_id=16384 AND patient_summary='TEST'")
        id = cursor.fetchone()
        patient.cancel_appointment(id[0], "2020-01-30", 2)
        self.assertEqual(helper_appointment(patient.cursor, id[0]), [(id[0], 16384, -2, patient.user_id, 'TEST',)])
        self.assertEqual(helper_avalibility(patient.cursor, 16384), [(16384, 2, '2020-01-30', 0)])
        cursor.execute("DELETE FROM appointment WHERE availability_id=16384 AND patient_summary='TEST'")
        conn.commit()


"""unit tests for user class """


class TestUserFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists("./store/UCLH.db"):
            from store.conn import create_database
            create_database()

    def test_login_wrong_parameters(self):
        from store.admin import Admin

        stranger = User.create_user()
        # Wrong email and password
        admin = stranger.login(stranger, "admin@mail.com", "PatientPassword")
        self.assertNotIsInstance(admin, Admin)
        self.assertEqual(admin.incorrect_password, True)
        admin = stranger.login(stranger, "wrongmail@mail.com", "wrongpassword")
        self.assertNotIsInstance(admin, Admin)
        self.assertEqual(admin.incorrect_email, True)

    def test_login_sanity(self):
        from store.patient import Patient
        from store.gp import GP

        stranger = User.create_user()
        # Other user login test
        patient = stranger.login(stranger, "patient@mail.com", "PatientPassword")
        self.assertIsInstance(patient, Patient)

        patient = stranger.login(stranger, "patient@mail.com", "wrongpassword")
        self.assertNotIsInstance(patient, Patient)

        gp = stranger.login(stranger, "gp@mail.com", "")
        self.assertNotIsInstance(gp, GP)

        gp = stranger.login(stranger, "gp@mail.com", "GpPassword")
        self.assertIsInstance(gp, GP)


class TestRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists("./store/UCLH.db"):
            from store.conn import create_database
            create_database()

    def test_registration_sanity(self):
        """ Test registration, function should handle replication of email."""
        from store.conn import connect_to_database
        Register.cursor.execute("DELETE FROM user WHERE email='testmail@mail.com'")
        Register.conn.commit()
        reg = Register.create_registration()
        # Create a record of user
        self.assertIsNone(
            Register.submit_registration(reg, "testmail@mail.com", "123456",
                                         "John", "raymond", "7376841",
                                         "london", "wc16bt", "2"))
        # Replicating record
        Register.cursor, Register.conn = connect_to_database()
        self.assertTrue(Register.email_already_exists(reg, "testmail@mail.com"))
        self.assertFalse(Register.email_already_exists(reg, "testmail@gmail.com"))

    def test_registration_check_parameters(self):
        # These emails should be invalid
        self.assertIsNone(Register.checkEmail(""))
        self.assertIsNone(Register.checkEmail("1234"))
        self.assertIsNone(Register.checkEmail("testmail.com"))
        self.assertIsNone(Register.checkEmail("testmail@"))
        self.assertIsNone(Register.checkEmail("testmail@.com"))
        self.assertIsNone(Register.checkEmail("testmail@com."))

        # These passwords should be invalid
        self.assertFalse(Register.checkPassword("123"))
        self.assertFalse(Register.checkPassword("123...."))
        self.assertFalse(Register.checkPassword(""))
