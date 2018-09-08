import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import urllib.request as urllib
import time
import socket

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

def averagePoints(L):
    if len(L) == 0:
        return Point(None,None)
    x_sum = 0
    y_sum = 0
    for x,y in L:
        x_sum += x
        y_sum += y
    return Point(x_sum / len(L), y_sum / len(L))

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
                # print(B0Coord)
            elif decodedObject.data.decode('utf-8') == B1_ID:
                B1Coord = averagePoints(decodedObject.polygon)
                # print(B1Coord)

    appendLastN(lastN, N, B0Coord, B1Coord)

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

def convertPositionsToInches(arenaInfo, lastN):
    nonNones = list(map(removeNones, lastN))
    B0Coord = nonNones[0][-1]
    B1Coord = nonNones[1][-1]

    B0InchesWidth = (B0Coord.x - arenaInfo["minX"])/arenaInfo["pixelsPerInchWidth"]
    B0InchesHeight = (B0Coord.y - arenaInfo["minY"])/arenaInfo["pixelsPerInchHeight"]

    B1InchesWidth = (B1Coord.x - arenaInfo["minX"])/arenaInfo["pixelsPerInchWidth"]
    B1InchesHeight = (B1Coord.y - arenaInfo["minY"])/arenaInfo["pixelsPerInchHeight"]

    returnList = list(map(str, [B0InchesWidth, B0InchesHeight, B1InchesWidth, B1InchesHeight]))

    return ";".join(returnList)


if __name__ == "__main__":

    ipc = ipCamera(SEE_URL)

    lastN = [[],[]]

    i = 0

    prevStable = False

    PRINT_THEM = False

    num_arrived = 0;

    hasBeenCalibrated = False

    seeSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    goSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    bindSocket(seeSocket, SEE_SOCKET_ADDRESS)

    while not hasBeenCalibrated:
        img = ipc.read()
        decodedObjects = decode(img)
        display(img, decodedObjects)

        arenaInfo, hasBeenCalibrated = calibrate(decodedObjects)

        if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
            break  # esc to quit


    while True:
        # if i % 10 == 0:
        #     PRINT_THEM = True
        # else:
        #     PRINT_THEM = False

        if (PRINT_THEM):
            print(i, "-----------------")

        img = ipc.read()
        decodedObjects = decode(img)

        display(img, decodedObjects)
        processDecodedObjects(lastN, MOVING_N, decodedObjects)

        if (PRINT_THEM):
            print("Last", MOVING_N, ":", lastN)
            print(averageLastN(lastN))

        stable = isStable(lastN, MOVING_N)

        if not(prevStable) and stable:
            print("~~~ARRIVED")
            num_arrived += 1
            sendToGoString = convertPositionsToInches(arenaInfo, lastN)
            print(sendToGoString)
            print(num_arrived,"-------------------")

            goSocket.sendto(sendToGoString.encode(), GO_SOCKET_ADDRESS)
            seeSocket.recv(10000)
            print("control returned")
            

        if prevStable and not(stable):
            print("~~~CHANGING")

        prevStable = stable

        if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
            break  # esc to quit

        if (PRINT_THEM):
            print()
            print()

        i += 1

    cv2.destroyAllWindows()
