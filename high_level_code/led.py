import serial
import socket, time
from constants import *
from common import *

# def setPlayerTurn():
#   leds.write('y'.encode())

# def setRobotTurn():
#     leds.write('r'.encode())

# def setChanging():
#     leds.write('t'.encode())


if __name__ == "__main__":
    leds = serial.Serial(port = LED_PORT, baudrate = 38400)
    ledSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    bindSocket(ledSocket, LED_SOCKET_ADDRESS)

    print("LISTENING FOR LED UPDATES")

    while True:
      buf = ledSocket.recv(10000)
      leds.write(buf)

