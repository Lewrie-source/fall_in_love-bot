import psycopg2
import logging
from datetime import *
import configparser


def connect_db():
    global cursor
    config = configparser.ConfigParser()
    config.read("config.ini")
    date = datetime.now().today()
    conn = psycopg2.connect(dbname="databasename", user="username", password="password", host="ip or url",
                            port="port")
    with conn.cursor() as cursor:
        print("⩾ Сonnected successfully")
    conn.autocommit = True  # устанавливаем актокоммит
    cursor = conn.cursor()
    if config['Bot']['logging'] == "True":
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s", handlers=[
                logging.FileHandler(f"logs/{date.day}.{date.month}.{date.year}.log"),
                logging.StreamHandler()
            ])
    else:
        logging.disable()


### Adds a record to the database
### check_existence - Checks if a record already exists in the database (True of False)
### Example of adding a record to a database: add_record("fil_bot", "fil", ["id", "partner_id"], [123, 321], check_existence=True)
def add_record(basename, tablename, columns = [], values = [], check_existence=False):
    if check_existence:
        exist_str = f"{columns[0]} = {values[0]} "
        for i in range(1, len(columns)):
            exist_str += f"AND {columns[i]} = {values[i]} "
        if get_record("fil_bot", "fil", selectable=f"{columns[0]}", columns=columns, values=values) == []:
            logging.info(f"ADDED NEW RECORD | database: {basename} | table: {tablename} | {columns} | {values}")
            cursor.execute(
                f'INSERT INTO "{basename}"."{tablename}" ({",".join(map(str, columns))}) VALUES ({",".join(map(str, values))})')
            return True
        else:
            return False
    else:
        logging.info(f"ADDED NEW RECORD | database: {basename} | table: {tablename} | {columns} | {values}")
        cursor.execute(
            f'INSERT INTO "{basename}"."{tablename}" ({",".join(map(str, columns))}) VALUES ({",".join(map(str, values))})')
        return True


###Retrieving a record from a database
def get_record(basename, tablename, selectable="*", columns=[], values=[]):
    if columns != [] and values != []:
        try:
            where_str = f"{columns[0]} = {values[0]} "
            for i in range(1, len(columns)):
                where_str += f"AND {columns[i]} = {values[i]} "
            cursor.execute(f'SELECT {selectable} FROM "{basename}"."{tablename}" WHERE {where_str}')
            return cursor.fetchall()
        except:
            where_str = f"{columns[0]} = '{values[0]}' "
            for i in range(1, len(columns)):
                where_str += f"AND {columns[i]} = '{values[i]}' "
            cursor.execute(f'SELECT {selectable} FROM "{basename}"."{tablename}" WHERE {where_str}')
            return cursor.fetchall()
    elif columns == [] and values == []:
        cursor.execute(f'SELECT {selectable} FROM "{basename}"."{tablename}"')
        return cursor.fetchall()
    else:
        logging.error(f"REQUEST ERROR")


def edit_record(basename, tablename, columns, values, where_column, where_value, method="str"):
    for i in range(0, len(columns)):
        try:
            cursor.execute(f'UPDATE "{basename}"."{tablename}" SET {columns[i]} = {values[i]} WHERE {where_column} = {where_value}')
        except:
            cursor.execute(
                    f"""UPDATE "{basename}"."{tablename}" SET {columns[i]} = '{values[i]}' WHERE {where_column} = {where_value}""")
    logging.info(
            f"EDITED RECORD | database: {basename} | table: {tablename} | {where_column} | {where_value} | {columns} | {values}")
