import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import urllib.request as urllib
import time

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
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')

    return decodedObjects

# Display barcode and QR code location
def display(im, decodedObjects):

  # Loop over all decoded objects
  for decodedObject in decodedObjects:
    points = decodedObject.polygon

    print(points)

    # If the points do not form a quad, find convex hull
    if len(points) != 4 :
        break;

    # Number of points in the convex hull
    n = len(points)

    # Draw the convext hull
    for j in range(0,n):
        cv2.line(im, points[j], points[ (j+1) % n], (0,255,0), 3)

  # Display results
  cv2.imshow("Results", im);

url='http://10.251.82.37:8080/shot.jpg'

SEE_WIDTH = 1440
SEE_HEIGHT = 1080

DO_WIDTH = 1280
DO_HEIGHT = 960

FRAME_DELAY = 3000

ESCAPE_KEY = 27


B0_INDEX = 0
B1_INDEX = 1

B0_ID = "b0"
B0_ID = "b1"

def appendLast5(last_5,B0Coords,B1Coords):
    last_5[0].append(B0Coords)
    if (len(last_5[0]) > 5):
        last_5[0].pop(0)

    last_5[1].append(B1Coords)
    if (len(last_5[1]) > 5):
        last_5[1].pop(0)

def removeNones(L):
    return list(filter(lambda x: x != None, L))

def averageLast5(last5):
    nonNones = map(removeNones, last5)
    return list(map(lambda x: sum(x) / len(x), nonNones))

def processDecodedObjects(last5, decodedObjects):
    B0Coords = None
    B1Coords = None
    for decodedObject in decodedObjects:
        if decodedObject.type == "QRCODE":
            if decodedObject.data.decode('utf-8') == B0_ID:
                pass
                # B0Coords = 


if __name__ == "__main__":

    ipc = ipCamera(url)

    # last5 = [[],[]]

    i = 0
    while True:
        print(i, "-----------------")
        img = ipc.read()
        decodedObjects = decode(img)
        display(img, decodedObjects)
        if cv2.waitKey(FRAME_DELAY) == ESCAPE_KEY:
            break  # esc to quit
        i += 1
        print()
        print()

    cv2.destroyAllWindows()
