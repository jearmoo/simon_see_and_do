import serial
from constants import ROBOT_PORT


ser = serial.Serial(port = ROBOT_PORT, baudrate = 38400)

def drop():
    ser.write('d'.encode())

def pickup():
    ser.write('p'.encode())

def forward(tenth_inches):
    b = (tenth_inches).to_bytes(4, byteorder = "little");
    b = 'f'.encode() + b
    ser.write(b)

def right(deg):
    b = (deg).to_bytes(4, byteorder = "little");
    b = 'r'.encode() + b
    ser.write(b)

def left(deg):
    b = (deg).to_bytes(4, byteorder = "little");
    b = 'l'.encode() + b
    ser.write(b)

def wait():
    while(ser.read() != 'A'.encode()):
        pass
