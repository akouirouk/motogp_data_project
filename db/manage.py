from mysql.connector import MySQLConnection
from sqlite3 import OperationalError
import mysql.connector

from configs.globals import MYSQL_USERNAME, MYSQL_PASSWORD
from logger import get_logger

# get sql logger
sql_log = get_logger(logger_name="sql_log", module_name=__name__)


def mysql_connect(host: str, db_name: str) -> MySQLConnection:
    """Connect to MySQL database

    Args:
        host (str): Host of the database
        db_name (str): The name of the database that you will be connecting to

    Raises:
        err: MySQL connection error

    Returns:
        MySQLConnection: The connection object to MySQL database
    """

    # try to connect to db
    try:
        # if db_name is NOT None
        if db_name != None:
            # connect to a mySQL db
            db = mysql.connector.connect(
                host=host,
                user=MYSQL_USERNAME,
                passwd=MYSQL_PASSWORD,
                database=db_name,
            )
        # if db_name is None
        else:
            # connect to a mySQL server (not a specific database on server)
            db = mysql.connector.connect(
                host=host,
                user=MYSQL_USERNAME,
                passwd=MYSQL_PASSWORD,
            )

        # return the db cursor object
        return db
    # if the connection has failed
    except mysql.connector.Error as err:
        # raise connection error
        raise err


def execute_sql_from_file(filename: str, conn: MySQLConnection) -> None:
    """Execute a SQL script from file

    Args:
        filename (str): Name of the file containing the SQL script
        conn (MySQLConnection): The connection object to MySQL database
    """

    # open and read the file as a single buffer
    fd = open(filename, "r")
    sql_file = fd.read()
    fd.close()

    # split SQL commands by ";"
    sql_commands = sql_file.split(";")

    # create cursor object
    with conn.cursor() as curr:
        # execute commands
        for command in sql_commands:
            try:
                curr.execute(command)
            # catch exception is there is an error with the SQL command
            except OperationalError as err:
                # log error
                sql_log.info(f"Command skipped: {err}")
