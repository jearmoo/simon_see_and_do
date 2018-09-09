import serial

leds = serial.Serial(port = "", baudrate = 38400)

def setPlayerTurn():
	leds.write('y'.encode())

def setRobotTurn():
	leds.write('r'.encode())

def setChanging():
	leds.write('t'.encode())