import mariadb
import dbcreds
import traceback
# https://thepythonguru.com/handling-errors/


def get_db_connection():
    # Create our connection to the DB and return it
    try:
        return mariadb.connect(user=dbcreds.user, password=dbcreds.password,
                               host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
    except mariadb.OperationalError:
        return None
    except mariadb.InternalError:
        return None
    except mariadb.DatabaseError:
        return None
    except mariadb.ProgrammingError:
        return None
    except:
        return None


def get_db_cursor(conn):
    # Get the cursor of the connection we have created
    try:
        return conn.cursor()
    except mariadb.OperationalError:
        return None
    except mariadb.InternalError:
        return None
    except mariadb.ProgrammingError:
        return None
    except mariadb.DatabaseError:
        return None
    except:
        return None


def close_db_cursor(cursor):
    # Close the passed in cursor
    if(cursor == None):
        # This means cursor is closed
        return True
    try:
        cursor.close()
        return True
    except mariadb.OperationalError:
        return False
    except mariadb.InternalError:
        return False
    except mariadb.ProgrammingError:
        return False
    except mariadb.DatabaseError:
        return False
    except:
        return False


def close_db_connection(conn):
    # Close the passed in connection
    if(conn == None):
        return True
    try:
        conn.close()
        return True
    except mariadb.OperationalError:
        return False
    except mariadb.InternalError:
        return False
    except mariadb.DatabaseError:
        return False
    except mariadb.ProgrammingError:
        return False
    except:
        return False
