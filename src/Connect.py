from pymongo import MongoClient

def connect():
    domain = 'domain.com'
    username = 'USERNAME'
    password = 'PASSWORD'
    authSource = 'user_table'
    return MongoClient(domain, 27017, username=username, password=password, authSource=authSource).finlab_dev
