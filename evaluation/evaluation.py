import json
import getpass
from pymongo import MongoClient


pwd = getpass.getpass("Password: ")
db = MongoClient(host="royceschultz.com", port=27017, username="finlab_beta", password=pwd, authSource="users").finlab_beta

def count_eval():
    col = db.MoodysValidateHeaders
    headers = list(col.find())
    correct = 0
    false_positive = 0
    false_negative = 0
    detection_count = 0
    header_count = 0
    correct_pages = 0
    for h in headers:
        if h['n_detections'] == h['n_headers']: 
            correct_pages += 1
        correct += min(h['n_detections'], h['n_headers'])
        false_positive += max(0, h['n_detections']-h['n_headers'])
        false_negative += max(0, h['n_headers']-h['n_detections'])
        detection_count += h['n_detections']
        header_count += h['n_headers']
    tp_rate = correct/header_count
    fp_rate = false_positive/header_count
    fn_rate = false_negative/header_count
    page_rate = correct_pages/len(headers)
    return tp_rate, fp_rate, fn_rate, page_rate


if __name__ == "__main__":
    print(count_eval())