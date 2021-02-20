import os
import re
from pymongo import MongoClient

def parse_OCR(path, page, year, brightness=60):
    '''
    Takes in a file path to a .zay file, page number, and year (optionally brightness)
    Returns a list of dictionaries each representing a ocr word detection
    '''
    res = []
    with open(path) as file:
        word_boxes = re.split('[\/[A-Za-z0-9-.]+\/*\.day', file.read())[brightness-1].strip().split('\n')
        for w in word_boxes:
            data = word_boxes.split(',')
            entry = {
                'x_1': int(data[1]),
                'x_2': int(data[2]),
                'y_1': int(data[3]),
                'y_2': int(data[4]),
                'text': data[-2],
                'brigtness': brightness,
                'page': page,
                'year': year
            }
            res.append(entry)
    return res

