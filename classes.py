from collections import namedtuple
import urllib.request as urllib
import cv2
import numpy as np

Point = namedtuple('Point', ['x', 'y'])

class ipCamera:
    def __init__(self, url):
        self.url = url

    def read(self):
        imgResp=urllib.urlopen(self.url)
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)
        return img
