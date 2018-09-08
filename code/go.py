import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import urllib.request as urllib
import time
import socket

from constants import *
from common import *


if __name__ == "__main__":

    ipc = ipCamera(GO_URL)

    i = 0

    PRINT_THEM = False

    num_arrived = 0;

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


    while True:
        img = ipc.read()
        decodedObjects = decode(img)

        markDecodedObjects(img, decodedObjects)

        blockCoordInfo = goSocket.recv(10000).decode()
        print(blockCoordInfo)

        display(img)

        if cv2.waitKey(FRAME_DELAY_MS) == ESCAPE_KEY:
            break  # esc to quit

        i += 1

    cv2.destroyAllWindows()
