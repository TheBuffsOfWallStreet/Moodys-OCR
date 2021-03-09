import getpass
from pymongo import MongoClient

def parse_header(path):
    '''
    Takes in a file path for the header data to be parsed
    Returns a list of dictionary objects of header data
    '''
    res = []
    with open(path) as file:
        lines = file.readlines()
        for line in lines:
            data = line.split(',')
            entry = {
                'company': data[0].strip('"'),
                'image_id': int(data[1]),
                'x1': float(data[2]),
                'x2': float(data[3]),
                'y1': float(data[4]),
                'y2': float(data[5])
            }
            res.append(entry)
    return res


if __name__ == "__main__":
    pwd = getpass.getpass("Password: ")
    headers = parse_header("GoldStandard1930s.20200923.csv")
    db = MongoClient(host="royceschultz.com", port=27017, username='finlab_beta', password=pwd, authSource="users").finlab_dev.yee_GoldHeaders
    db.insert_many(headers)