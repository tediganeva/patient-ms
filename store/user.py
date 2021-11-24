import hashlib

from store.storage import Storage


class User(Storage):
    """ The Register class groups methods and state for the users logged into the application.

    This class will be the entrypoint for logging users into the system and returning a newly 
    instantiated Admin or GP or Patient class depending on the login credentials.

    Attributes:
        first_name (string): the first name of the user who logs in.
        last_name (string): the family name of the user who logs in.
        email (string): the email address of the user who logs in.
        user_id (integer): the unique user id of the user who logs in.
        user_role_id (integer): the role of the user logging in (0: Admin, 1: GP, 2: Patient).
        user_status_id (integer): the account status of the user who attemps to log in. (-1: Deactivated, 0: Pending Activation, 1: Activated).
        incorrect_email (bool): state that signifies whether an incorrect email was supplied during login.
        incorrect_password (bool): state that signifies whether an incorrect password was supplied during login.
    """

    def __init__(self):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit state and methods from the Storage class.
        super().__init__()

        # first_name is the first name of the user who logs on. This value is initially set to None
        # and reset to None if the user has logged out.
        self.first_name = None

        # last_name is the family name of the user who logs on. This value is initially set to None
        # and reset to None if the user has logged out.
        self.last_name = None

        # email is the email address of the user who logs on. This value is initially set to None 
        # and reset to None if the user has logged out.
        self.email = None
    
        # user_id is the id of the user who logs on. This value is initially set to None if the 
        # user has not logged on or has logged out or it is 'x' where x > 0 to match the auto 
        # incrementing primary key within the database.
        self.user_id = None

        # the user_role_id is updated after the user logs in and reflects who the user is within 
        # the duration of the application. This makes it so that the user can be validated and that 
        # validation stored without without further (wasteful) queries to the database to determine 
        # whether a user can perform an action.
        self.user_role_id = None

        # the user_status_id is updated after the user logs in and also reflects who the user is
        # duration of the application.
        self.user_status_id = None

        # incorrect_email is changed if the user has submitted an incorrect email
        self.incorrect_email = False

        # incorrect_password is changed if the user has submitted an incorrect password.
        self.incorrect_password = False


    @classmethod
    def create_user(cls):
        """ Creates a new instance of the User class.

        This method creates a new instance of the User class. This is the primary method of class
        instantiation. This creates a new instance after using the inherited Storage class to
        establish a connection to the database and embed the required sqlite3.connection and 
        sqlite3.cursor objects within it.

        Returns:
            cls (User): A new instance of the Register class with query-enabled internal variables.
        """

        # create an instance of the storage class object.
        store = Storage

        # establish a connection, create the database and embed the connection and cursor object 
        # within the store class.
        store._establish_connection(store)

        # return an instance of the User class using the store
        return cls


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


    def compare_password(self, email, password):
        """ Compares user supplied password with one stored in the database.

        This method should be called only after verifying that the user exists in the database.

        Args:
            email (string): the users email address.
            password (string): the users email address.

        Returns:
            bool: 'True' if the password is correct and 'False' if not.
        """

        # database query
        statement = "SELECT password FROM user WHERE email = '{}'".format(email)
        lookup = self.cursor.execute(statement)

        # returns a list, get the first value from the list.
        stored_hashed_password = lookup.fetchone()

        # if the password does
        if stored_hashed_password == None:
            return False

        # hash the user supplied password and compare to the stored hashed password.
        incoming_hashed_password = hashlib.sha1(password.encode('utf-8')).hexdigest()

        # compare the stored hash with the incoming has and return either True or false depending
        # on whether the passwords are the same.
        if stored_hashed_password[0] != incoming_hashed_password:
            return False

        else:
            return True
        

    def login(self, user_email, password):
        """ Logs the user into the application.

        This method, depending on the user supplied credentials, logs the user into the system. It
        is a constructor that returns a new child class (Admin, GP or Patient) if the login was 
        successful or itself if not successful.

        Args:
            user_email (string): the users email address.
            password (string): the users password used for access verification.

        Returns:
            Admin (Admin): A new instance of the Admin class that inherits from self.
            GP (GP): A new instance of the GP class that inherits from self.
            Patient (Patient): A new instance of the Admin class that inherits from self.
            self (User): The same instance of the user class with updated internal state.
        """

        # verify that the email exists in the database.
        email_exists = self.email_already_exists(self, user_email)

        # if the supplied email does not exist update internal incorrect_email variable and return User.
        if email_exists == False:
            self.incorrect_email = True
            self.email = None
            self.user_id = None
            self.user_role_id = None
            self.incorrect_password = False

            return self

        # check if the user supplied password for the email is correct.
        password_valid = self.compare_password(self, user_email, password)

        # if the supplied password does not exist update internal incorrect_password variable and return User.
        if password_valid == False:
            self.incorrect_password = True
            self.email = None
            self.user_id = None
            self.user_role_id = None
            self.incorrect_email = False
            return self

        # user now verified; grab the user_id and user_role_id from the database and update the
        # internal state. Return either an Admin, GP or Patient depending on the returned credentials.

        # database query
        statement = """
            SELECT user_id, user_role_id, user_status_id, first_name, last_name 
            FROM user 
            WHERE email = '{}'""".format(user_email)

        lookup = self.cursor.execute(statement)

        # returns a list, get the first value from the list.
        result = lookup.fetchall()

        # update the internal user_id state using the results of the query.
        self.email = user_email

        # update the internal user_id state using the results of the query.
        self.user_id = result[0][0]

        # update the internal user_role state using the results of the query.
        self.user_role_id = result[0][1]

        # update the internal user_status_id state using the results of the query.
        self.user_status_id = result[0][2]

        # update the internal first_name state using the results of the query.
        self.first_name = result[0][3]

        # update the internal last_name state using the results of the query.
        self.last_name = result[0][4]

        # explicitly set incorrect_email state to False.
        self.incorrect_email = False

        # explicitly set incorrect_password state to False.
        self.incorrect_password = False

        # if user is an admin return the Admin class to the caller.
        if self.user_role_id == 0:
            from store.admin import Admin
            return Admin(self)

        # if user is an GP return the GP class to the caller.
        elif self.user_role_id == 1:
            from store.gp import GP
            return GP(self)

        # user is therefore a Patient return the Patient class to the caller
        else: 
            from store.patient import Patient
            return Patient(self)
