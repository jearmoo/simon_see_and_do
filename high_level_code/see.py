import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import urllib.request as urllib
import time
import socket
import json

from constants import *
from common import *

def appendLastN(lastN,N,B0Coord,B1Coord):
    lastN[0].append(B0Coord)
    if (len(lastN[0]) > N):
        lastN[0].pop(0)

    lastN[1].append(B1Coord)
    if (len(lastN[1]) > N):
        lastN[1].pop(0)

def removeNones(L):
    return list(filter(lambda x: x != None, L))

def averageLastN(lastN):
    nonNones = map(removeNones, lastN)
    return list(map(lambda x: averagePoints(x), nonNones))

def processDecodedObjects(lastN, N, decodedObjects):
    B0Coord = None
    B1Coord = None
    for decodedObject in decodedObjects:
        if decodedObject.type == "QRCODE":
            if decodedObject.data.decode('utf-8') == B0_ID:
                B0Coord = averagePoints(decodedObject.polygon)
            elif decodedObject.data.decode('utf-8') == B1_ID:
                B1Coord = averagePoints(decodedObject.polygon)

    appendLastN(lastN, N, B0Coord, B1Coord)

# checks if a points is within epsilon of the given avg
def withinEpsilon(p,avg,eps):
    return abs(p.x - avg.x) <= eps and abs(p.y - avg.y) <= eps

def average(L):
    return sum(L) / len(L)

def isStable(lastN, N):
    B0WithoutNones = removeNones(lastN[0])
    B1WithoutNones = removeNones(lastN[1])

    # has to be more than 2 non-none values in last 5 recorded points
    if len(B0WithoutNones) <= 2 or len(B1WithoutNones) <= 2:
        return False

    B0Average = averagePoints(B0WithoutNones)
    B1Average = averagePoints(B1WithoutNones)

    if (len(list(filter(lambda x: not(withinEpsilon(x,B0Average,STABLE_EPSILON)), B0WithoutNones))) > 0 or
        len(list(filter(lambda x: not(withinEpsilon(x,B1Average,STABLE_EPSILON)), B1WithoutNones))) > 0):
        return False

    return True

# MUST BE IN A STABLE STATE
def getBlockCoords(lastN):
    nonNones = list(map(removeNones, lastN))
    B0Coord = nonNones[0][-1]
    B1Coord = nonNones[1][-1]
    return [B0Coord, B1Coord]

def serializeBlockCoords(B0Inches, B1Inches):
    return json.dumps([B0Inches.x, B0Inches.y, B1Inches.x, B1Inches.y]).encode('utf-8')

def addArrivedText(img):
    cv2.putText(img, "ARRIVED", Point(0,SEE_HEIGHT), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 2)

def addChangingText(img):
    cv2.putText(img, "CHANGING", Point(0,SEE_HEIGHT), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 2)

if __name__ == "__main__":

    ipc = ipCamera(SEE_URL)

    lastN = [[],[]]

    prevStable = False

    num_arrived = 0;

    hasBeenCalibrated = False

    seeSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    goSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    ledSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    bindSocket(seeSocket, SEE_SOCKET_ADDRESS)

    while not hasBeenCalibrated:
        img = ipc.read()
        decodedObjects = decode(img)
        markDecodedObjects(img, decodedObjects)

        arenaInfo, hasBeenCalibrated = calibrate(decodedObjects)

        display(img)

        if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
            break  # esc to quit

    print("CALIBRATED!")

    lastStableB0Coord = None
    lastStableB1Coord = None

    while True:

        img = ipc.read()
        decodedObjects = decode(img)

        markDecodedObjects(img, decodedObjects)

        processDecodedObjects(lastN, MOVING_N, decodedObjects)

        stable = isStable(lastN, MOVING_N)

        if not(prevStable) and stable:
            num_arrived += 1
            print(num_arrived,"-------------------")
            print("~~~ARRIVED")
            lastStableB0Coord, lastStableB1Coord = getBlockCoords(lastN)
            print(lastStableB0Coord, lastStableB1Coord)
            B0Inches, B1Inches = convertCoordsToInches(arenaInfo, lastStableB0Coord, lastStableB1Coord)
            print(B0Inches, B1Inches)

            print(serializeBlockCoords(B0Inches,B1Inches))

            saveTmpImage(img)

            ledSocket.sendto("r".encode(), LED_SOCKET_ADDRESS)
            goSocket.sendto(serializeBlockCoords(B0Inches, B1Inches), GO_SOCKET_ADDRESS)
            seeSocket.recv(10000)
            ledSocket.sendto("y".encode(), LED_SOCKET_ADDRESS)
            print("control returned")

        # I'm printing the coord that was last marked as stable because this is what the robot will go off of
        if stable:
            ledSocket.sendto("y".encode(), LED_SOCKET_ADDRESS)
            markBlockCoord(img,lastStableB0Coord)
            markBlockCoord(img,lastStableB1Coord)
            addArrivedText(img)

        if prevStable and not(stable):
            print("~~~CHANGING")
            ledSocket.sendto("t".encode(), LED_SOCKET_ADDRESS)

        if not(stable):
            addChangingText(img)

        prevStable = stable

        # put arena info on image
        markArenaCornerCoords(img, arenaInfo)

        # Display image
        display(img)

        if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
            break  # esc to quit

    cv2.destroyAllWindows()
