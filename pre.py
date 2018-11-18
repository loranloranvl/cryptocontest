import mysql.connector
import logging
import json

formatStr = '%(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, filename='crypto.log', filemode='w', format=formatStr)

logFormatter = logging.Formatter(formatStr)
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler(filename='crypto.log', mode='w')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

db = None
cursor = None

def db_connect():
    global db
    global cursor
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="MYsql123!",
        database="crypto",
        buffered=True
    )
    cursor = db.cursor()
    assert cursor != None
    return (db, cursor)

def insert(sql):
	cursor.execute(sql)
	db.commit()

def select(sql):
	cursor.execute(sql)
	db.commit()
	return cursor.fetchall()

db_connect()

success_res = json.dumps({
    'status': '200',
    'msg': ''
})

error_res = lambda msg: json.dumps({
    'status': '200',
    'msg': msg
})