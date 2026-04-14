import os
from contextlib import contextmanager

import pyodbc
import os
from dotenv import load_dotenv
import psycopg2




load_dotenv(dotenv_path=os.environ.get("envipath"))



DB_NAME =  os.environ.get("DB_NAME")
DB_USER =  os.environ.get("DB_USER")
DB_PASSWORD =  os.environ.get("DB_PASSWORD")
DB_HOST =  os.environ.get("DB_HOST")



conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# connection_string = (
#         'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + db_name + ';UID=' + user_name + ';PWD=' + password + ';MARS_Connection=' + con)
# connection_string = (
#     'DRIVER={ODBC Driver 17 for SQL Server};'
#     f'SERVER={DB_HOST};'
#     f'DATABASE={DB_NAME};'
#     f'UID={DB_USER};'
#     f'PWD={DB_PASSWORD};'
#     'Encrypt=no;'
#     'TrustServerCertificate=yes;'
# )


# def get_db_cursor(is_common=True):
#     conn = pyodbc.connect(connection_string, autocommit=True)
#     cursor = conn.cursor()
#     try:
#         yield cursor
#     finally:
#         # pass
#         # print("Finally db connection closed!")
#         if is_common:
#             cursor.close()
#             conn.close()


def get_db_cursor():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()

    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()