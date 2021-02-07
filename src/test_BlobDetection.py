def test_importable():
    import BlobDetection

def test_num_blobs_detected():
    from BlobDetection import maskImage, detectBlobs
    import numpy as np
    image = 255 * np.ones((100,100)) # White background (page)
    for i in range(0,len(image),10): # 10 spaced out black boxes (text)
        image[i:i+3, i:i+3] = 0
    mask = maskImage(image)
    blobs = detectBlobs(mask)
    assert len(blobs) == 10
