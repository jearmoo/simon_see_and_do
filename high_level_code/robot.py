import serial
from constants import ROBOT_PORT
import time


ser = serial.Serial(ROBOT_PORT, baudrate = 38400)



def wait():
    while(ser.read() != 'A'.encode()):
        time.sleep(.1)

def extra_wait():
    wait()
    time.sleep(1.5)

def drop():
    ser.write('d'.encode())
    extra_wait()

def pickup():
    ser.write('p'.encode())
    extra_wait()

def forward(tenth_inches):
    if tenth_inches == 0:
        return
    b = (tenth_inches).to_bytes(4, byteorder = "little");
    b = 'f'.encode() + b
    ser.write(b)
    extra_wait()

def backwards(tenth_inches):
    if tenth_inches == 0:
        return
    b = (tenth_inches).to_bytes(4, byteorder = "little");
    b = 'b'.encode() + b
    ser.write(b)
    extra_wait()

def right(deg):
    b = (deg).to_bytes(4, byteorder = "little");
    b = 'r'.encode() + b
    ser.write(b)
    extra_wait()

def left(deg):
    b = (deg).to_bytes(4, byteorder = "little");
    b = 'l'.encode() + b
    ser.write(b)
    extra_wait()

if __name__ == "__main__":
    print("connected")
    #while True:
    #    forward(60)
    #    left(127)
