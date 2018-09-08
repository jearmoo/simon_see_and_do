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
def markDecodedObjects(im, decodedObjects):
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

    return im

def bindSocket(socket, socketAddress):
    if os.path.exists(socketAddress):
        os.remove(socketAddress)
    socket.bind(socketAddress)

ArenaInfo = namedtuple('ArenaInfo', ['topLeft', 'bottomRight', 'pixelsPerInchWidth', 'pixelsPerInchHeight'])

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

        arenaInfo = ArenaInfo(Point(minX,minY), Point(maxX,maxY), (maxX - minX)/ARENA_WIDTH, (maxY - minY)/ARENA_HEIGHT)


    return arenaInfo, isCalibrated

def display(img, scale=.4):
    # Display image
    small = cv2.resize(img,(0,0),fx=scale,fy=scale)
    cv2.imshow("Results", small);

def markBlockCoord(img, coord):
    # radius is 20, color is red (b,g,r),-1 means a filled circle instead of outline
    cv2.circle(img, (int(coord.x), int(coord.y)), 20, (0,0,255), -1)

def markArenaCorner(img, coord):
    cv2.circle(img, (int(coord.x), int(coord.y)), 10, (255,0,0), -1)

def markArenaCornerCoords(img, arenaInfo):
    markArenaCorner(img, arenaInfo.topLeft)
    markArenaCorner(img, arenaInfo.bottomRight)

def pixelCoordToInches(coord, topLeft, pixelToInchWidth, pixelToInchHeight):
    return Point((coord.x-topLeft.x)/pixelToInchWidth,(coord.y-topLeft.y)/pixelToInchHeight)

def convertCoordsToInches(arenaInfo, B0Coord, B1Coord):
    B0Inches = pixelCoordToInches(B0Coord, arenaInfo.topLeft, arenaInfo.pixelsPerInchWidth, arenaInfo.pixelsPerInchHeight)
    B1Inches = pixelCoordToInches(B1Coord, arenaInfo.bottomRight, arenaInfo.pixelsPerInchWidth, arenaInfo.pixelsPerInchHeight)
    return [B0Inches, B1Inches]

