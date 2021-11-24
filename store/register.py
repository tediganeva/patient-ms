import hashlib
import logging
import re
import sqlite3

from store.storage import Storage


class Register(Storage):
    """ The Register class groups methods and state required to register into the application. """

    def __init__(self):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit state and methods from the Storage class.
        super().__init__()


    @classmethod
    def create_registration(cls):
        """ Creates a new instance of the Register class.

        This method creates a new instance of the Register class. This is the primary method of
        class instantiation. This creates a new instance after using the inherited Storage class to
        establish a connection to the database and embed the required sqlite3.connection and
        sqlite3.cursor objects within it.

        Returns:
            cls (Register): A new instance of the Register class with query-enabled internal variables.
        """

        # create an instance of the storage class object.
        store = Storage

        # establish a connection, create the database and embed the connection and cursor object
        # within the store class.
        store._establish_connection(store)

        # create an instance of the User class using the store
        return cls


    @staticmethod
    def checkEmail(email):
        """ Validates the email is correct for registration.

        Args:
            email (string): the users' email

        Returns:
            bool: 'True' if the email is valid and 'False' if not.
        """

        # use regular expressions
        return re.match('^[a-zA-Z0-9_.]+@[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+$', email)


    @staticmethod
    def checkPassword(password):
        """ Validates the user supplied password.

        This method verifies that the user supplied password for registration contains only
        alphanumeric characters and is between 5 and 10 characters long.

        Args:
            password (string): the users password

        Returns:
            bool: 'True' if the password is valid and 'False' if not.
        """
        # use regular expressions
        return re.match('[a-zA-Z0-9_]{5,10}$', password)


    @staticmethod
    def checkPhonenumber(phonenumber):
        """ Validates the phone number.

        This method verifies that the phone number for registration contains exactly 11 digits and
        begins with "07".

        Args:
            phonenumber (string): the users' phone number

        Returns:
            bool: 'True' if the phone number is valid and 'False' if not.
        """
        # use regular expressions
        return re.match('^07[0-9]{9}$', phonenumber)


    def email_already_exists(self, email):
        """ Validates email uniqueness.

        This method checks whether the supplied email already exists in the database.

        Args:
            email (string): the users email address.

        Returns:
            bool: 'True' if the email is already exists and 'False' if not.
        """

        # database query statement
        statement = "SELECT EXISTS(SELECT 1 FROM user WHERE email = '{}')".format(email)
        lookup = self.cursor.execute(statement)
        row = lookup.fetchone()
        # if the same email was found in the database return True
        if row[0] == 1:
            return True
        elif row[0] == 0:
            return False


    def submit_registration(self, email, password, firstname, lastname, phone, location, address, role):
        """ Inserts a registration into the database.

        This function inserts a new user into the database and set the user_status to 0 (Pending
        Activation) for the Admin to later approve or reject.
        """

        try:
            self.cursor.execute('''INSERT INTO user (email,password,first_name,last_name,phone_num,
                                                    location,address,user_status_id,user_role_id)
                                    VALUES (?,?,?,?,?,?,?,?,?)''',
                                                    (email, hashlib.sha1(password.encode('utf-8')).hexdigest(),
                                                    firstname, lastname, phone,
                                                    location, address, 0, role))
            self.conn.commit()
            self.conn.close()

        except sqlite3.Error as er:
            logging.warning(er)
