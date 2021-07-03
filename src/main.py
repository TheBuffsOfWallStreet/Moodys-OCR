'''
NOT PRODUCTION READY
Probably won't even run without syntax errors.
Just a skeleton to improve later.
'''

from Connect import connect
from OCRModel import predictWordBounds
import BlobDetection
import Clustering

db = connect()
word_db = db.OCR_word_boxes
cluster_db = db.OCR_clusters

def loadImage(image_url):
    raise NotImplementedError

for page in word_db.find({'image_url': {'$exists': True}}):
    # Detect Blobs (paragraphs/columns) for a given page.
    image = loadImage(page['image_url'])
    mask = BlobDetection.maskImage(image)
    blob_bounds = detectBlobBounds(mask)

    # Save blob_bounds to database?

    # Cluster words within each blob
    for i, blob in enumerate(blob_bounds):
        pipeline = [
            # Select words on current page
            {'$match': {'_id': page['_id']}},
            # Unwind word boxes on page
            {'$unwind': {'path': '$words'}}
            # Select words within current blob bounds
            {'$match': {
                'words.center_x': {
                    '$gt': blob['x_min'],
                    '$lt': blob['x_max'],
                },
                'words.center_y': {
                    '$gt': blob['y_min'],
                    '$lt': blob['y_max']
                }
            }}
        ]
        words = [word for word in word_db.aggregate(pipeline)]
        distances = Clustering.calculateWordDistanceMatrix(words)
        clusters = clusterWords(words, distances, max_distace=blob['width']/3, max_loops=1000)

        # Save clusters to database
        for cluster in clusters:
            cluster_db.insert({
                'page_id': page['_id'],
                'blob_id': i,
                'word_ids': cluster,
            })

    # Assemble clusters from each blob into a complete page
    pipeline = [
        # Select current page
        {'$match': {'page_id': page['_id']}},
        # Join word_db
        {'$lookup' {
            'from': 'Word_db',
            'localField': 'word_ids',
            'foreignField' '_id',
            'as': 'matched_words'
        }},
        # Add cluster bound information
        {'$project': {
            'blob_id': 1,
            'matched_words': 1,
            'max_bounds': {'$max': '$matched_words.opp_origin'},
            'min_bounds': {'$min': '$matched_words.origin'}
        }},
        # Unwind on words
        {'$unwind': {'path': '$matched_words'}},
        # Sort by x position
        {'$sort': {'matched_words.origin_x': 1}},
        # Group by cluster_id, now each group is a cluster that is sorted in normal left-to-right reading order.
        {'$group': {
            '_id': '$_id',
            'blob_id': {'$first': '$blob_id'},
            'origin': {'$first': '$min_bounds'},
            'words': {'$push': '$matched_words.word'},
            'x': {'$push': '$matched_words.origin_x'}
        }},
        # Sort by y position
        {'$sort': {'origin.1': 1}},
        # Group by blob_id
        {'$group': {
            '_id': '$blob_id',
            'paragraph': {'$push': '$words'}
        }}
    ]
    paragraphs = []
    for paragraph in cluster_db.aggregate(pipeline):
        position = blob_bounds[paragraph['_id']]['origin']
        score = np.dot(position, (0.1, 1))
        paragraph_string = '\n'.join([
            ' '.join(line) for line in blob['paragraph']
        ])
        paragraphs.append((score, paragraph_string))

    output_db.insert({
        'page_id': page['_id'],
        'text': '------\n'.join(paragraphs)
    })
