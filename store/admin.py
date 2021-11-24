from store.user import User
from store.send_email_gmail import *


class Admin(User):
    """ The Admin class groups methods required for the functionality of an Admin user. 

    The Admin class inherits from Login. This class will be the entrypoint to methods that only the
    Admins within the system have access to.
    """

    def __init__(self, User):
        """ Instatiates the class and inherited initializes internal variables. """

        # inherit state and methods from the User class.
        User().__init__()


    def manage_records(self, view_filter):
        """ Gets a list of all users in the database. 

        Args:
            view_filter (string): additional information to provide filtering of the user table to
                get specific views i.e. view all pending GP's or view all deactivated Patient's etc.

        Returns:
            result (list): resultset of executing an SQL query.
        """

        # database query (space left at the end for additional filtering based on admin input).
        statement = """
            SELECT user_id, email, first_name, last_name, phone_num, location, address, user_status_name, user_role_name 
            FROM user, user_status, user_role
            WHERE user.user_status_id = user_status.user_status_id 
            AND user.user_role_id = user_role.user_role_id """

        # apply any filters on the view that the admin sees depending on their input. If no filters
        # were selected then all records are selected by default.
        if view_filter == '' or view_filter == 'All':
            statement = statement + "AND user.user_role_id != 0" 

        elif view_filter == 'Pending GPs':
            statement = statement + "AND user.user_status_id = 0 AND user.user_role_id = 1"

        elif view_filter == 'Pending Patients':
            statement = statement + "AND user.user_status_id = 0 AND user.user_role_id = 2"

        elif view_filter == 'Active GPs':
            statement = statement + "AND user.user_status_id = 1 AND user.user_role_id = 1"

        elif view_filter == 'Active Patients':
            statement = statement + "AND user.user_status_id = 1 AND user.user_role_id = 2"

        elif view_filter == 'Deactivated GPs':
            statement = statement + "AND user.user_status_id = -1 AND user.user_role_id = 1"

        elif view_filter == "Deactivated Patients":
            statement = statement + "AND user.user_status_id = -1 AND user.user_role_id = 2"

        # return the result of the query execution to the caller
        return self.cursor.execute(statement)


    def delete_user(self, user_id):
        """ Deletes a record from the user database

        Args:
            user_id (string): the user id of a user in the system.
        """

        # database query
        statement = """
            DELETE FROM user
            WHERE user_id = '{}'""".format(user_id)

        # execute the statement.
        self.cursor.execute(statement)

        self.conn.commit()


    def activate_user(self, user_id):
        """ Activates a newly registered user in the database.

        This method updates the user_status_id of a specified user from 0 (Pending Activation) to 1
        (Activated).

        Args:
            user_id (string): the user id of a user in the system.
        """

        # database query
        statement = """
            UPDATE user 
            SET user_status_id = 1 
            WHERE user_id = '{}'""".format(user_id)

        # execute the statement.
        self.cursor.execute(statement)

        self.conn.commit()


    def deactivate_user(self, user_id):
        """ Activates a newly registered user in the database.

        Args:
            user_id (string): the user id of a user in the system.
        """

        # database query
        statement = """
            UPDATE user 
            SET user_status_id = -1 
            WHERE user_id = '{}'""".format(user_id)

        # execute the statement.
        self.cursor.execute(statement)

        self.conn.commit()


    def send_emails_patients(self, option):
        """Sends emails to patients for pending or not pending appointments.

        Args:
            option (string): the status of the next day appointment.
        """

        if option == "pending":
            emails(0, self.conn, self.cursor)

        elif option == "not_pending":
            emails(1, self.conn, self.cursor)
            emails(-1, self.conn, self.cursor)
