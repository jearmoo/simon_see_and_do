import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import urllib.request as urllib
import time
import socket
import math
from pathplanning import calcRobotPath
import json

from constants import *
from common import *

def processGoDecodedObjects(decodedObjects):
    B0Coord = None
    B1Coord = None
    RFCoord = None
    RBCoord = None
    for decodedObject in decodedObjects:
        if decodedObject.type == "QRCODE":
            if decodedObject.data.decode('utf-8') == B0_ID:
                B0Coord = averagePoints(decodedObject.polygon)
            elif decodedObject.data.decode('utf-8') == B1_ID:
                B1Coord = averagePoints(decodedObject.polygon)
            elif decodedObject.data.decode('utf-8') == RF_ID:
                RFCoord = averagePoints(decodedObject.polygon)
            elif decodedObject.data.decode('utf-8') == RB_ID:
                RBCoord = averagePoints(decodedObject.polygon)

    return [B0Coord, B1Coord, RFCoord, RBCoord]

if __name__ == "__main__":

    ipc = ipCamera(GO_URL)

    hasBeenCalibrated = False

    seeSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    goSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    bindSocket(goSocket, GO_SOCKET_ADDRESS)

    while not hasBeenCalibrated:
        img = ipc.read()
        decodedObjects = decode(img)
        markDecodedObjects(img, decodedObjects)

        arenaInfo, hasBeenCalibrated = calibrate(decodedObjects)

        display(img)

        if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
            break  # esc to quit

    print("CALIBRATED!")

    while True:
        blockCoordInfo = goSocket.recv(10000).decode()
        goalInfo = json.loads(blockCoordInfo.decode('utf-8'))

        B0Goal = Point(goalInfo[0], goalInfo[1])
        B1Goal = Point(goalInfo[2], goalInfo[3])

        # TODO: get the position of the robot and blocks
        foundEverything = False
        # [B0Avg, B1Avg, RFAvg, RBAvg]
        coords = [None, None, None, None]
        while not(foundEverything):
            img = ipc.read()
            decodedObjects = decode(img)
            markDecodedObjects(img, decodedObjects)
            coordinates = processGoDecodedObjects(decodedObjects)

            for i in range(len(coords)):
                if coords[i] == None:
                    coords[i] = coordinates[i]

            if not(None in coords):
                foundEverything = True

            # put arena info on image
            markArenaCornerCoords(img, arenaInfo)
            display(img)

            if cv2.waitKey(5000) == ESCAPE_KEY:
                break

        print("FOUND EVERYTHING")

        img = ipc.read()
        B0Coord,B1Coord,RFCoord,RBCoord = coords

        markRobotCoords(img, RFCoord, RBCoord)

        # calculate the robot's rotation
        robotRotation = calcRobotRotation(RFCoord,RBCoord)

        # find what we have to move

        

        path = calcRobotPath(RFCoord, RBCoord, B0Coord, B1Coord)

        # TODO: plan the path

        # TODO: draw the path

        # TODO: tell see code we're done
        display(img)

        if cv2.waitKey(5000) == ESCAPE_KEY:
            break
    seeSocket.sendto(b'', SEE_SOCKET_ADDRESS)




    # cv2.destroyAllWindows()
