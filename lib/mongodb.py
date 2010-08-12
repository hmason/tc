import logging
from pymongo import *

def connect(dbname, port=27017):
    logging.debug("connecting to magicbus mongodb")
    conn = connection.Connection('localhost', port)
    db = database.Database(conn, dbname)
    return db