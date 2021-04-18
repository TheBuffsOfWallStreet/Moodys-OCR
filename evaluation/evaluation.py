import json
import getpass
import numpy as np
from pymongo import MongoClient
import matplotlib.pyplot as plt


# pwd = getpass.getpass("Password: ")
pwd = "efficientmarkets"
db = MongoClient(host="royceschultz.com", port=27017, username="finlab_beta", password=pwd, authSource="users").finlab_beta

def count_eval():
    '''
    Compares the counts of the detections and headers per page. 
    Returns true positive, false positive, false negative, and correct page rates.
    This method assumes that every detection is correct up to the limit of correct headers per page.
    '''
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

def w_man_dist(c1, c2, wx=0.1, wy=0.9):
    '''
    Calculates the weighted manhattan distance between the
    two imput coordinates
    '''
    return wx*abs(c1[0]-c2[0]) + wy*abs(c1[1]-c2[1])

def det_center(detection):
    '''
    Calculates center of detection
    '''
    x = np.mean([detection['min'][0], detection['max'][0]])
    y = np.mean([detection['min'][1], detection['max'][1]])
    return [x, y]

def dist_eval(dist_tol=60, sample_size=None):
    '''
    If a sample_size is given will take a random sample of gold headers. If not will grab all the 
    gold headers. Then, the gold headers are compared with detections using a weighted manhattan
    distance. Returns the count of golden headers that match a detection, number of golden headers,
    and list of minimum distances of each header to detections.
    '''
    correct = 0
    n = 0
    m_dist = []
    if sample_size:
        gold_headers = list(db.MoodysGoldHeaders.aggregate([{"$sample": {"size": sample_size}}]))
    else:
        gold_headers = list(db.MoodysGoldHeaders.find())
    for g in gold_headers:
        detections = db.MoodysDetectionBoxes.find_one({'_id': g['_id']})
        for h in g['headers']:
            if detections and detections['detections']:
                try:
                    distances = [w_man_dist(h['raw_center'], det_center(d)) for d in detections['detections']]
                    m_dist.append(min(distances))
                    if min(distances) < dist_tol:
                        correct += 1
                except KeyError:
                    pass
            n += 1
    return correct, n, m_dist

if __name__ == "__main__":
    print(count_eval())
    correct, n, distances = dist_eval()
    print(correct/n)
    plt.hist(distances, bins=25)
    plt.show()