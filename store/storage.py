# import database connection and creation methods only.
from store.conn import connect_to_database


class Storage:
    """ The Storage class groups methods and state required to connect to the database.

    Storage defines the top level class that is used within the store package, all other classes
    within store will either directly or by inheritance import the Storage class to get access to
    the internal sqlite3.connection and sqlite3.cursor objects from the sqlite3 package. These
    objects can then be efficiently re-used across the application create queries to the datastore
    without having to expensively close and reopen a connection.

    Attributes:
        conn (sqlite3.connection): sqlite3 class object obtained from connecting to the database.
        cursor (sqlite3.cursor): sqlite3 class object to enable querying the database.
    """

    def __init__(self):
        """ Instatiates the class and initializes internal variables. """

        # internal sqlite3.connection object is set to 'None' as no connection has been established.
        self.conn = None

        # internal sqlite3.cursor object is set to 'None' as no connection has been established.
        self.cursor = None


    def _establish_connection(self):
        """ Established a connection to the database and creates the schema if necessary

        This method both creates the tables required for operation of the application and creates
        new tables if the database does not yet have data within it. This method is private and
        should not be used directly outside the store library. This method takes self as a first 
        parameter, after calling the method it then updates the internal state of itself, this 
        'wires-up' the conn and cursor objects enabling them for use in querying the database.
        """

        # get sqlite3 connection and cursor objects from by invoking functions in conn.py
        conn, cursor = connect_to_database()

        # assign conn and cursor to internal object governed by the Storage class.
        self.conn = conn
        self.cursor = cursor
