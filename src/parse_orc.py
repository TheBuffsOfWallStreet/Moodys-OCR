import os
import re
import time
import getpass
import argparse
from pymongo import MongoClient

def parse_OCR(path, page, year, brightness):
    '''
    Takes in a file path to a .zay file, page number, and year (optionally brightness)
    Returns a list of dictionaries each representing a ocr word detection
    '''
    res = []
    with open(path) as file:
        if brightness:
            word_boxes = re.split('[\/[A-Za-z0-9-.]+\/*\.day', file.read())[brightness-1].strip().split('\n')
            for w in word_boxes:
                data = w.split(',')
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
        else:
            ocr_runs = re.split('[\/[A-Za-z0-9-.]+\/*\.day', file.read())
            for i, run in enumerate(ocr_runs):
                word_boxes = run.strip().split('\n')
                for w in word_boxes:
                    data = w.split(',')
                    entry = {
                        'x_1': int(data[1]),
                        'x_2': int(data[2]),
                        'y_1': int(data[3]),
                        'y_2': int(data[4]),
                        'text': data[-2],
                        'brigtness': i,
                        'page': page,
                        'year': year
                    }
                    res.append(entry)
    return res

def insert_year(path, year, brightness):
    '''
    Input directory path to OCR data and year of book
    Ex:
        path: "/scratch/summit/diga9728/Moodys/Industrials/OCRrun1936/"
        year: 1936
    Inserts the OCR data from parsed files into database
    '''
    pwd = getpass.getpass("Password: ")
    db = MongoClient(host="royceschultz.com", port=27017, username="finlab_beta", password=pwd, authSource="users").finlab_dev.asy_MoodysOCR
    dirs = os.listdir(path)
    sub_dirs = []
    for d in dirs:
        match = re.fullmatch('[0-9]{3}', d)
        if match:
            sub_dirs.append(match.group(0))
    for d in sub_dirs:
        sub_path = os.path.join(path, d)
        files = os.listdir(sub_path)
        for f in files:
            if '.zay' in f:
                print(f)
                try:
                    page = int(f[-8:-4])
                    docs = parse_OCR(os.path.join(sub_path, f, brightness), page, year)
                    db.insert_many(docs)
                except Exception as e:
                    print(f)
                    print(e)

if __name__ == "__main__":
    '''
    Parse command line arguements for file path and year of book being parsed
    Parse data for that year and insert into database
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to parent directory of OCR files", type=str)
    parser.add_argument("year", help="year of the book being parsed", type=int)
    parser.add_argument("-b", dest="brightness", default=None, help="brightness level to be used if none given will use all", type=int)
    args = parser.parse_args()
    start_time = time.time()
    insert_year(args.path, args.year, args.brightness)
    end_time = time.time()
    print("Runtime: {} sec".format(end_time-start_time))