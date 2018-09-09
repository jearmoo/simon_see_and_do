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
from robot import *

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
        blockCoordInfo = goSocket.recv(10000)
        finalPosInfo = json.loads(blockCoordInfo.decode('utf-8'))

        # originalPosInfo = processGoDecodedObjects(decodedObjects)

        B0GoalInches = Point(goalInfo[0], goalInfo[1])
        B1GoalInches = Point(goalInfo[2], goalInfo[3])

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
        markBlockCoord(img, B0Coord):
        markBlockCoord(img, B1Coord):
        markArenaCornerCoords(img, arenaInfo)

        display(img)


        # find what we have to move

        B0CoordInches = pixelCoordToInches(arenaInfo, B0Coord)
        B1CoordInches = pixelCoordToInches(arenaInfo, B1Coord)
        RFCoordInches = pixelCoordToInches(arenaInfo, RFCoord)
        RBCoordInches = pixelCoordToInches(arenaInfo, RBCoord)

        distB0 = distance (B0GoalInches, B0CoordInches)
        distB1 = distance (B1GoalInches, B1CoordInches)


        blockMoved = distB0 > distB1 ? (B0_ID, B0GoalInches) : (B1_ID, B1GoalInches)

        RCenterCoord = averagePoints([RFCoordInches, RBCoordInches])
        path = calcRobotPath(RCenterCoord, B0CoordInches, B1CoordInches, blockMoved)

        # if there is no path, continue and wait for another instruction
        if (path == None or len(path) <= 1):
            print("NO PATH")
            seeSocket.sendto(b'', SEE_SOCKET_ADDRESS)
            continue

        # draw the path
        drawPath(img, RCenterCoord, path)

        # calculate the robot's rotation
        robotRotation = calcRotation(RFCoord,RBCoord)

        prevRobotRotation = robotRotation
        prevPathPoint = (RCenterCoord.x, RCenterCoord.y)
        buffer = []

        print("EXECUTE THE PATH")
        for i in range(1,len(path)):
            if (path[i] == "pickup" or path[i] == "drop"):
                moveDistance = sum(buffer)
                buffer = []
                # send movedistance
                forward(int(moveDistance * 10))
                wait()
                if (path[i] == "pickup"):
                    pickup()
                    wait()
                if (path[i] == "drop"):
                    drop()
                    wait()
                continue


            pathRotation = calcRotation(path[i], prevPathPoint)
            angleDiff = thDiff(pathRotation, prevRobotRotation)

            if (angleDiff != 0):
                moveDistance = sum(buffer)
                buffer = []

                rotateAmount = math.degrees(angleDiff)

                # send over commands
                forward(int(moveDistance * 10))
                wait()
                if rotateAmount > 0:
                    right(rotateAmount)
                    wait()
                else:
                    left(-rotateAmount)
                    wait()

            buffer.append(distance(path[i],prevPathPoint))
            prevPathPoint = path[i]
            prevRobotRotation = pathRotation

        # this should never happen
        if len(buffer) > 0:
            moveDistance = sum(buffer)
            print("This should never happen happened")
            forward(int(moveDistance * 10))
            wait()

        if cv2.waitKey(5000) == ESCAPE_KEY:
            break

        print("PATH EXECUTED")

        seeSocket.sendto(b'', SEE_SOCKET_ADDRESS)


    cv2.destroyAllWindows()
    ser.close()
