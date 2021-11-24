import hashlib
import logging
import os
import platform
import sqlite3


def connect_to_database():
    """ Connects to the database file and instantiates sqlite3

    This function opens and connects to the sqlite3 database. This function is private and should
    not be used directly outside the store library. If no existing database is found in the store
    directory the user will recieve a warning and a new database will automatically be created.

    Returns:
        conn (sqlite3.connection): sqlite3 class object obtained from connecting to the database.
        cursor (sqlite3.cursor): sqlite3 class object to enable querying the database.
    """

    # the database file should reside in the below location (under the store/ directory).
    database_path = os.path.join(os.path.abspath(os.getcwd()), 'store', 'UCLH.db')

    # attempt to 
    try:
        # connect to the database and create a sqlite3.conn object
        conn = sqlite3.connect(database_path)

        # create a sqlite3.cursor object
        cursor = conn.cursor()

        # return both to the caller.
        return conn, cursor

        # if the database does not yet exist
    except:
        # log the error
        logging.warning("Database creation / connection error.")

        # exit and raise the correct errorcode to the user.
        if platform.system() == 'Windows':
            # Raise ERROR_FILE_NOT_FOUND (The system cannot find the file specified)
            os._exit(2)

        elif platform.system() == 'Linux':
            # Raise ENONET (no such file or directory)
            os._exit(2)

        else:
            # Raise fnfErr (file not found)
            os._exit(-43)


def create_database():
    """ Creates the backend database schema.

    This function creates the tables required for operation of the application. The function is 
    private and should not be used directly outside the store library. If the database already has
    the required tables up and running this function does nothing.
    """

    # calling connect to db to create conn and cursor:
    conn, cursor = connect_to_database()

    # the user_status table stores whether an account is pending activation, active or deactivated.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_status (
            user_status_id integer PRIMARY KEY,
            user_status_name text
        )
    """)

    # the user_role table stores whether the user is an admin, gp or patient.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_role (
            user_role_id INTEGER PRIMARY KEY,
            user_role_name TEXT
        )
    """)

    # the user table stores general information about users within the system, the users can either 
    # be admins that manage the application, gp's or patients.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password BLOB,
            first_name TEXT,
            last_name TEXT,
            phone_num TEXT,
            address TEXT,
            location TEXT,
            user_status_id INTEGER,
            user_role_id INTEGER,

            FOREIGN KEY (user_status_id) 
                REFERENCES user_status (user_status_id),
            FOREIGN KEY (user_role_id) 
                REFERENCES user_role (user_role_id)
        )
    """)

    # the availability_status stores whether a potential appointment datetime is available or not.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability_status (
            availability_status_id INTEGER PRIMARY KEY,
            availability_status_name TEXT
        )
    """)

    # the availability table stores availability information that gp's enter and patients can 
    # select from, once an appointment is unavailable the status is updated here.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            datetime TEXT,
            availability_status_id INTEGER,

            FOREIGN KEY (doctor_id)
                REFERENCES user (user_id)
                ON DELETE CASCADE 
                ON UPDATE CASCADE,
            FOREIGN KEY (availability_status_id)
                REFERENCES availability_status (availability_status_id)
        )
    """)

    # the appointment_status table stores information about a pending / ended appointment. The 
    # status of an appointment is updated based on whether the appointment was missed, cancelled by 
    # the patient or gp, pending confirmation by the gp, confirmed, completed without the gp 
    # providing a prescription or completed with the gp providing a prescription.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment_status (
            appointment_status_id INTEGER PRIMARY KEY,
            appointment_status_name TEXT
        )
    """)

    # the appointment table stores appointment information that can be viewed and updated by both 
    # gp's and patients. Depeninging on who views it, there are several actions that can be taked 
    # to update the status of an appointment.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            availability_id INTEGER,
            appointment_status_id INTEGER,
            patient_id INTEGER,
            patient_summary TEXT,

            FOREIGN KEY (availability_id)
                REFERENCES availability (availability_id)
                ON DELETE CASCADE 
                ON UPDATE CASCADE,
            FOREIGN KEY (appointment_status_id)
                REFERENCES appointment_status (appointment_status_id),
            FOREIGN KEY (patient_id)
                REFERENCES user (user_id)
                ON DELETE CASCADE 
                ON UPDATE CASCADE
        )
    """)

    # the prescription table stores information about a completed appointment and is an area for 
    # the gp to prescribe medecine to the patient based on what was determined in the appointment.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_record (
            medical_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER,
            prescription_info TEXT,
            diagnosis TEXT,
            doctors_comment TEXT,

            FOREIGN KEY (appointment_id)
                REFERENCES appointment (appointment_id)
                ON DELETE CASCADE 
                ON UPDATE CASCADE
        )
    """)

    # create table operations must be committed prior to insertions.
    conn.commit()

    # seed the user_status key and values into the database.
    cursor.execute("""
        INSERT OR IGNORE INTO user_status (user_status_id, user_status_name)
        VALUES 
            (-1, 'DEACTIVATED'),
            (0, 'PENDING ACTIVATION'),
            (1, 'ACTIVATED')
    """)

    # seed the user_role key and values into the database.
    cursor.execute("""
        INSERT OR IGNORE INTO user_role (user_role_id, user_role_name)
        VALUES 
            (0, 'ADMIN'), 
            (1, 'GP'),
            (2, 'PATIENT')
    """)

    # seed the availability_status key and values into the database.
    cursor.execute("""
        INSERT OR IGNORE INTO availability_status (availability_status_id, availability_status_name)
        VALUES 
            (0, 'AVAILABLE'), 
            (1, 'UNAVAILABLE')
    """)

    # seed the appointment_status key and values into the database.
    cursor.execute("""
        INSERT OR IGNORE INTO appointment_status (appointment_status_id, appointment_status_name)
        VALUES 
            (-4, 'CANCELLED BY SYSTEM'),
            (-3, 'MISSED BY PATIENT'), 
            (-2, 'CANCELLED BY PATIENT'),
            (-1, 'CANCELLED BY GP'),
            (0, 'PENDING CONFIRMATION'), 
            (1, 'CONFIRMED'), 
            (2, 'COMPLETED WITHOUT PRESCRIPTION'),
            (3, 'COMPLETED WITH PRESCRIPTION'),
            (4, 'GP ACTION REQUIRED')
    """)

    # insert an initialized Admin.
    admin_pass = 'AdminPassword'
    hash_admin_pass = hashlib.sha1(admin_pass.encode('utf-8')).hexdigest()

    statement = """
        INSERT OR IGNORE INTO user (
            email,
            password,
            first_name,
            last_name,
            phone_num,
            address,
            location,
            user_status_id,
            user_role_id
        ) 
        VALUES (
            'admin@mail.com',
            '{}',
            'AdminBro',
            'AdminSmith',
            '07965434794',
            'admin avenue',
            'London',
            1,
            0)""".format(hash_admin_pass)

    cursor.execute(statement)

    # insert an initialized GP.
    gp_pass = 'GpPassword'
    hash_gp_pass = hashlib.sha1(gp_pass.encode('utf-8')).hexdigest()

    statement = """
        INSERT OR IGNORE INTO user (
            email,
            password,
            first_name,
            last_name,
            phone_num,
            address,
            location,
            user_status_id,
            user_role_id
        ) 
        VALUES (
            'gp@mail.com',
            '{}',
            'GpHuman',
            'GpSmith',
            '07965434794',
            'gp grange',
            'London',
            1,
            1)""".format(hash_gp_pass)

    cursor.execute(statement)

    # insert an initialized Patient.
    patient_pass = 'PatientPassword'
    hash_patient_pass = hashlib.sha1(patient_pass.encode('utf-8')).hexdigest()

    statement = """
        INSERT OR IGNORE INTO user (
            email,
            password,
            first_name,
            last_name,
            phone_num,
            address,
            location,
            user_status_id,
            user_role_id
        ) 
        VALUES (
            'patient@mail.com',
            '{}',
            'Patience',
            'PatientSmith',
            '07965434794',
            'patient parade',
            'London',
            1,
            2)""".format(hash_patient_pass)

    cursor.execute(statement)

    # enable foreign key usage within sqlite3.
    cursor.execute("""
        PRAGMA foreign_keys = ON
    """)

    # enable automatic compaction upon deleting rows within the database to save space.
    cursor.execute("""
        PRAGMA auto_vacuum = FULL
    """)

    # commit insertion operations
    conn.commit()


# if the file is run as main, the above two methods are called to generate the conn and cursor
# objects and to enable unit tests.
conn, cursor = connect_to_database()
create_database()
