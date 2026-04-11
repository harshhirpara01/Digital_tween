import os
import pyodbc
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(dotenv_path=os.environ.get("envipath"))

mongoliink = os.environ.get("mongoliink")
user_name = os.environ.get("user_name")
password = os.environ.get("password")
server = os.environ.get("server")
db_name = os.environ.get("db_name")
con = 'Yes'
# connection_string = (
#         'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + db_name + ';UID=' + user_name + ';PWD=' + password + ';MARS_Connection=' + con)
connection_string = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={db_name};'
    f'UID={user_name};'
    f'PWD={password};'
    'Encrypt=no;'
    'TrustServerCertificate=yes;'
)
conn = pyodbc.connect(connection_string, autocommit=True, Pooling=True)

mongo_username = os.environ.get("mongo_username")
mongo_password = os.environ.get("mongo_password")
mongo_host = os.environ.get("mongo_host")
mongo_port = os.environ.get("mongo_port")
mongo_databasename = os.environ.get("mongo_databasename")

client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_databasename}')
mdb = client[f"{mongo_databasename}"]

# client = MongoClient(f'mongodb://{mongo_host}:{mongo_port}/{mongo_databasename}')
# mdb = client[f"{mongo_databasename}"]

##########################44444444444444444444444444444444444

user_name = 'nex_arbritage_2025'
password = '4mdknsltvbizrexucwjf'
server = '185.139.228.238'
db_name = 'nex_arbritage_2025'

# connection_string = (
#         'DRIVER={ODBC Driver 18 for SQL Server};SERVER=' + server + ';DATABASE=' + db_name + ';UID=' + user_name +
#         ';PWD=' + password)
