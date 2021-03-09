import getpass
from pymongo import MongoClient

def parse_header(path):
    with open(path) as file:
        lines = file.readlines()
        