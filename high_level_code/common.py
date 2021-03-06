from collections import namedtuple
import urllib.request as urllib
import pyzbar.pyzbar as pyzbar
import cv2
import numpy as np
import os
import math
import time

from constants import *

Point = namedtuple('Point', ['x', 'y'])

def pointToIntPoint(point):
    return Point(int(point.x), int(point.y))

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

def display(img, scale=.4, name="Results"):
    # Display image
    small = cv2.resize(img,(0,0),fx=scale,fy=scale)
    cv2.imshow(name, small);

def markBlockCoord(img, coord):
    # radius is 20, color is red (b,g,r),-1 means a filled circle instead of outline
    cv2.circle(img, pointToIntPoint(coord), 20, (0,0,255), -1)

def markArenaCorner(img, coord):
    cv2.circle(img, pointToIntPoint(coord), 10, (255,0,0), -1)

def markArenaCornerCoords(img, arenaInfo):
    markArenaCorner(img, arenaInfo.topLeft)
    markArenaCorner(img, arenaInfo.bottomRight)

def markRobotCoords(img, front, back):
    # front is purple and back is yellow
    cv2.circle(img, pointToIntPoint(front), 10, (255,0,255), -1)
    cv2.circle(img, pointToIntPoint(back), 10, (0,255,255), -1)

# point is an (x,y) tuple
def markPathSegment(img, arenaInfo, point1, point2):
    lineBegin = inchCoordToPixels(arenaInfo, point1)
    lineEnd = inchCoordToPixels(arenaInfo, point2)

    # print(lineBegin, lineEnd)
    cv2.line(img, lineBegin, lineEnd, (255,0,0), 3)

def drawPath(img, arenaInfo, path):
    # path[0] = (RCenterCoord.x,RCenterCoord.y)
    prev = path[0]
    print(path)
    # prev = RCenterCoord
    for i in range(1,len(path)):
        if not isinstance(path[i], str):
            markPathSegment(img, arenaInfo, Point(*prev), Point(*path[i]))
            prev = path[i]

# returns inch coordinates from top left of field
def pixelCoordToInches(arenaInfo, coord):
    return Point((coord.x-arenaInfo.topLeft.x)/arenaInfo.pixelsPerInchWidth,(coord.y-arenaInfo.topLeft.y)/arenaInfo.pixelsPerInchHeight)

# coord is a tuple
def inchCoordToPixels(arenaInfo, coord):
    return pointToIntPoint(Point(coord.x*arenaInfo.pixelsPerInchWidth + arenaInfo.topLeft.x, coord.y * arenaInfo.pixelsPerInchHeight + arenaInfo.topLeft.y))
    # return Point((coord.x-arenaInfo.topLeft.x)/arenaInfo.pixelsPerInchWidth,(coord.y-arenaInfo.topLeft.y)/arenaInfo.pixelsPerInchHeight)

def convertCoordsToInches(arenaInfo, B0Coord, B1Coord):
    B0Inches = pixelCoordToInches(arenaInfo, B0Coord)
    B1Inches = pixelCoordToInches(arenaInfo, B1Coord)
    return [B0Inches, B1Inches]

def markQuad(img ,quad):
    # Draw the quad
    n = len(quad)
    for j in range(0,n):
        cv2.line(im, pointToIntPoint(quad[j]), pointToIntPoint(quad[ (j+1) % n]), (0,255,0), 3)

def thDiff(th2, th1):
    return math.atan2(math.sin(th2-th1), math.cos(th2-th1));

def calcRotation(frontCoord, backCoord):
    # ydif = frontCoord.y - backCoord.y
    # xdif = frontCoord.x - backCoord.x

    # if (xdif == 0):
    #     if ydif > 0:
    #         return -math.pi / 2
    #     elif ydif < 0:
    #         return math.pi / 2
    #     else:
    #         return 0

    # if (ydif == 0):
    #     if xdif > 0:
    #         return 0
    #     elif xdif < 0:
    #         return -math.pi
    #     else:
    #         return 0

    # return -math.atan2(ydif / xdif, xdif / ydif)

    ydif = abs(backCoord.y - frontCoord.y)
    xdif = abs(backCoord.x - frontCoord.x)

    try:
        angle = math.atan2(ydif, xdif)
    except:
        angle = math.pi/2

    if (frontCoord.y > backCoord.y):
        if (frontCoord.x > backCoord.x):
            angle *= -1
        else:
            angle -= math.pi
    else:
        if (frontCoord.x < backCoord.x):
            angle = math.pi - angle

    return angle


def averagePoints(L):
    if len(L) == 0:
        return Point(None,None)
    x_sum = 0
    y_sum = 0
    for x,y in L:
        x_sum += x
        y_sum += y
    return Point(x_sum / len(L), y_sum / len(L))

def distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def pointsEqual(point1, point2):
    point1.x == point2.x and point1.y == point2.y

if __name__ == "__main__":
    blank_image = np.zeros((500,500,3), np.uint8)
    arenaInfo = ArenaInfo(Point(0,0),Point(0,0),5, 5)
    drawPath(blank_image, arenaInfo, Point(2,2), [(2,2), (2,4), (2,55), (70,55), (70,22)])
    display(blank_image, .5)
    cv2.waitKey(0)

def saveTmpImage(img):
    cv2.imwrite("/tmp/" + str(time.time()) + ".png", img)