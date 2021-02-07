import numpy as np
import PIL
import cv2


def maskImage(im):
    '''
    @param {PIL.Image} im - Input Image
    @return black and white 'thresholded' image selecting for black text
    '''
    im_array = np.asarray(im).astype(float)

    scalar = int(0.01 * max(im_array.shape)) # Scales to handle both large and small images
    if scalar % 2 == 0:
        scalar += 1
    # Blur
    blur = cv2.GaussianBlur(im_array,(scalar,scalar),0)
    # Threshold
    ret,threshold = cv2.threshold(blur.astype('uint8'), thresh=220, maxval=255, type=1)
    # Dilate
    n = scalar // 2
    dilate = cv2.dilate(threshold, np.ones((n,n)).astype('uint8'))
    # Blur
    blur = cv2.GaussianBlur(dilate,(scalar,scalar),0)
    # Threshold
    ret,threshold = cv2.threshold(blur.astype('uint8'), thresh=150, maxval=255, type=0)

    return np.asarray(threshold)


def neighbors(x, y, im_shape):
    '''
    helper function for graph search in detectBlobs.
    @return list of 2-4 valid neighbors around a given (x,y) point
    '''
    n = []
    if x > 0:
        n.append((x-1, y))
    if y > 0:
        n.append((x, y-1))
    if x < im_shape[0] - 1:
        n.append((x+1, y))
    if y < im_shape[1] - 1:
        n.append((x, y+1))
    return n


def detectBlobs(image_mask):
    '''
    Identifies contiguous white blobs on a black background
    @param {np.array[][]} image_mask - thresholded image
    @return list of blobs. Each blob is a list of pixels.
    '''
    blobs = []
    seen = np.zeros(image_mask.shape)
    m, n = image_mask.shape
    for x in range(m):
        print(f'{x / m:.2%}, found {len(blobs)} blobs', end='\r')
        for y in range(n):
            if image_mask[x][y] > 0 and seen[x][y] == 0:
                q = [(x, y)]
                new_blob = []
                while q:
                    x, y = q.pop(0)
                    for i, j in neighbors(x, y, image_mask.shape):
                        if image_mask[i][j] > 0 and seen[i][j] == 0:
                            seen[i][j] = 1
                            new_blob.append([i, j])
                            q.append((i, j))
                blobs.append(new_blob)
    return blobs
