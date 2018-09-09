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

def findRobotRotation(ipc, arenaInfo):

    # RFAvg, RBAvg
    coords = [None, None]

    foundEverything = False
    while not(foundEverything):
        img = ipc.read()
        decodedObjects = decode(img)
        markDecodedObjects(img, decodedObjects)
        coordinates = processGoDecodedObjects(decodedObjects)[2:]

        for i in range(len(coords)):
            if coords[i] == None:
                coords[i] = coordinates[i]

        if not(None in coords):
            foundEverything = True

        # put arena info on image
        # print(arenaInfo)
        markArenaCornerCoords(img, arenaInfo)
        display(img, .4, "rotation calibration")

        if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
            break

    return calcRotation(coords[0], coords[1])

def calibrateRotation(ipc, arenaInfo, goalRotation):
    print("CALIBRATING ROTATION TO", goalRotation)
    robotRotation = findRobotRotation(ipc, arenaInfo)
    theta_diff = thDiff(goalRotation, robotRotation)
    while abs(theta_diff) > ROTATION_TOLERANCE:
        print(theta_diff)
        rotateAmount = int(math.degrees(theta_diff))
        if rotateAmount > 0:
            print("left", rotateAmount)

            if (COMMAND_ROBOT):
                left(rotateAmount)

            
                
        else:
            print("right", -rotateAmount)

            if (COMMAND_ROBOT):
                right(-rotateAmount)
        robotRotation = findRobotRotation(ipc,arenaInfo)
        theta_diff = thDiff(goalRotation, robotRotation)


if __name__ == "__main__":

    ipc = ipCamera(GO_URL)

    hasBeenCalibrated = False

    seeSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    goSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    bindSocket(goSocket, GO_SOCKET_ADDRESS)

    print("-------CALIBRATING")


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
        print("WAITING ON SEE CODE")
        blockCoordInfo = goSocket.recv(10000)
        goalInfo = json.loads(blockCoordInfo.decode('utf-8'))

        print("RECEIVED THE GOAL ", goalInfo)

        B0GoalInches = Point(goalInfo[0], goalInfo[1])
        B1GoalInches = Point(goalInfo[2], goalInfo[3])

        # TODO: get the position of the robot and blocks
        foundEverything = False
        # [B0Avg, B1Avg, RFAvg, RBAvg]
        coords = [None, None, None, None]

        print("FINDING BIG BRAINS")
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
            # print(arenaInfo)
            markArenaCornerCoords(img, arenaInfo)
            display(img)

            if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
                break

        print("FOUND EVERYTHING")

        img = ipc.read()
        B0Coord,B1Coord,RFCoord,RBCoord = coords

        markRobotCoords(img, RFCoord, RBCoord)
        markBlockCoord(img, B0Coord)
        markBlockCoord(img, B1Coord)
        markArenaCornerCoords(img, arenaInfo)

        


        # find what we have to move

        B0CoordInches = pixelCoordToInches(arenaInfo, B0Coord)
        B1CoordInches = pixelCoordToInches(arenaInfo, B1Coord)
        RFCoordInches = pixelCoordToInches(arenaInfo, RFCoord)
        RBCoordInches = pixelCoordToInches(arenaInfo, RBCoord)

        distB0 = distance (B0GoalInches, B0CoordInches)
        distB1 = distance (B1GoalInches, B1CoordInches)

        if (distB0 < 2 and distB1 < 2):
            seeSocket.sendto(b'sup', SEE_SOCKET_ADDRESS)
            print("DISTANCE MOVED IS TOO SMALL, CONTROL RETURNED")
            continue

        blockMoved = (B0_ID, B0GoalInches) if distB0 > distB1 else (B1_ID, B1GoalInches)

        RCenterCoord = averagePoints([RFCoordInches, RBCoordInches])

        print("PLANNING PATH")
        path = calcRobotPath(RCenterCoord, B0CoordInches, B1CoordInches, blockMoved)
        print("PATH PLANNED!")

        # print("CALCULATED A PATH")

        # if there is no path, continue and wait for another instruction
        if (path == None or len(path) <= 1):
            print("NO PATH")
            seeSocket.sendto(b'', SEE_SOCKET_ADDRESS)
            continue

        # draw the path
        drawPath(img, arenaInfo, path)

        # display the img
        display(img)
        saveTmpImage(img)

        if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
            break

        # # calculate the robot's rotation
        robotRotation = calcRotation(RFCoord,RBCoord)


        prevRobotRotation = robotRotation
        # prevPathPoint = (RCenterCoord.x, RCenterCoord.y)
        prevPathPoint = path[0]
        buffer = []

        print("EXECUTE THE PATH")
        for i in range(1,len(path)):
            if (path[i] == "pickup" or path[i] == "drop"):
                moveDistance = sum(buffer)
                buffer = []

                reducedMove = max(int(moveDistance * 10) - FINAL_REDUCTION_TENTH_INCHES,0)
                print("forward", reducedMove)

                if (COMMAND_ROBOT):
                    forward(reducedMove)
                    

                if (path[i] == "pickup"):
                    print("pickup")
                    if (COMMAND_ROBOT):
                        pickup()

                    
                        
                if (path[i] == "drop"):
                    print("drop")
                    if (COMMAND_ROBOT):
                        drop()
                continue


            pathRotation = calcRotation(Point(*path[i]), Point(*prevPathPoint))
            angleDiff = thDiff(pathRotation, prevRobotRotation)

            if (angleDiff != 0):
                moveDistance = sum(buffer)
                buffer = []

                rotateAmount = int(math.degrees(angleDiff))

                # send over commands
                print("forward", int(moveDistance * 10))

                if (COMMAND_ROBOT):
                    forward(int(moveDistance * 10))

                
                

                if rotateAmount > 0:

                    print("left", rotateAmount)

                    if (COMMAND_ROBOT):
                        left(rotateAmount)

                    
                        
                else:
                    print("right", -rotateAmount)

                    if (COMMAND_ROBOT):
                        right(-rotateAmount)

                if (CALIBRATE_ROTATION):
                    calibrateRotation(ipc, arenaInfo, pathRotation)

                    
                        

            buffer.append(distance(Point(*path[i]),Point(*prevPathPoint)))
            prevPathPoint = path[i]
            prevRobotRotation = pathRotation

        # this should never happen
        if len(buffer) > 0:
            moveDistance = sum(buffer)
            print("This should never happen happened")
            print("forward", int(moveDistance * 10))

            if (COMMAND_ROBOT):
                forward(int(moveDistance * 10))              

            

        print("PATH EXECUTED")

        # print("PATH EXECUTED")

        seeSocket.sendto(b'sup', SEE_SOCKET_ADDRESS)


    cv2.destroyAllWindows()
    ser.close()
