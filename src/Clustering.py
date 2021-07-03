import numpy as np

def calculateWordDistanceMatrix(words):
    '''
    @param {list[{}]} words - word boundries generated from an image.
    @return 2d array of all pairwise distances between words.
    Measures distance between the end of a word and the start of another word.
    Note: Dist[i][j] != Dist[j][i].
    Ignores identity distance by seting it to max distance.
    '''
    num_words = len(words)
    dists = np.zeros((num_words, num_words))
    for i in range(num_words):
        for j in range(num_words):
            if i != j:
                loc_a = words[i]['origin'].copy()
                loc_a[0] += words[i]['width']
                loc_b = words[j]['origin']
                delta = np.subtract(loc_a, loc_b)
                if delta[0] < 0:
                    delta[0] *= 2
                delta[1] *= 3
                distance = np.linalg.norm(delta)
                dists[i][j] = distance
    max_dist = dists.max()
    for i in range(num_words):
        dists[i][i] = max_dist + 1
    return dists

def clusterWords(words, dists, max_distance=0, max_loops=1000):
    '''
    Merges words into larger clusters in order of least distance.
    Repeats until max_loops reached or distance exceeds max_distance.
    @return {list[][]} returns a list of clusters. Each cluster is a list of word '_id' fields.
    '''
    clusters = [[word['_id']] for word in words]
    cluster_dists = dists.copy()
    max_loops = min(len(clusters) - 1, max_loops)

    for n_loop in range(max_loops):
        # Get location of minimum remaining distance
        i, j = np.unravel_index(cluster_dists.argmin(), cluster_dists.shape)
        d = cluster_dists[i,j]
        if max_distance and d > max_distance:
            break
        clusters[i] = clusters[i] + clusters[j]
        del clusters[j]
        cluster_dists[i] = cluster_dists[j]
        # cluster_dists[:,i] goes unchanged
        cluster_dists = np.delete(cluster_dists, j, axis=0)
        cluster_dists = np.delete(cluster_dists, j, axis=1)
    return clusters
