from collections import namedtuple
import urllib.request as urllib
import pyzbar.pyzbar as pyzbar
import cv2
import numpy as np
import os

from constants import *

Point = namedtuple('Point', ['x', 'y'])

class ipCamera:
    def __init__(self, url):
        self.url = url

    def read(self):
        imgResp=urllib.urlopen(self.url)
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)
        return img

def decode(im) :
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)

    # Print results
    # for obj in decodedObjects:
    #     print('Type : ', obj.type)
    #     print('Data : ', obj.data,'\n')

    return decodedObjects

# Display barcode and QR code location
def display(im, decodedObjects):
    # Loop over all decoded objects
    for decodedObject in decodedObjects:
        points = decodedObject.polygon
        #print(points)

        # If the points do not form a quad, find convex hull
        if len(points) != 4 :
            break;

        # Number of points in the convex hull
        n = len(points)

        # Draw the convext hull
        for j in range(0,n):
            cv2.line(im, points[j], points[ (j+1) % n], (0,255,0), 3)

    # Display results
    small = cv2.resize(im,(0,0),fx=.6,fy=.6)
    cv2.imshow("Results", small);

def bindSocket(socket, socketAddress):
    if os.path.exists(socketAddress):
        os.remove(socketAddress)    
    socket.bind(socketAddress)

def calibrate(decodedObjects):
    c0points = None
    c1points = None

    isCalibrated = False

    arenaInfo = {}

    for decodedObject in decodedObjects:
        if decodedObject.type == "QRCODE":
            if decodedObject.data.decode('utf-8') == C0_ID:
                c0points = decodedObject.polygon
            elif decodedObject.data.decode('utf-8') == C1_ID:
                c1points = decodedObject.polygon

    if (c0points != None and c1points != None):
        isCalibrated = True

        minX = 10**6
        minY = 10**6
        maxX = -1
        maxY = -1

        allPoints = c0points + c1points

        for point in allPoints:
            minX = min(point.x, minX)
            minY = min(point.y, minY)

            maxX = max(point.x, maxX)
            maxY = max(point.y, maxY)

        arenaInfo["minX"] = minX
        arenaInfo["minY"] = minY
        arenaInfo["maxX"] = maxX
        arenaInfo["maxY"] = maxY

        arenaInfo["pixelsPerInchHeight"] = (maxY - minY)/ARENA_HEIGHT
        arenaInfo["pixelsPerInchWidth"] = (maxX - minX)/ARENA_WIDTH


    return arenaInfo, isCalibrated
