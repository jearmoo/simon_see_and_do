import serial

ser = serial.Serial(port = "COM3", baudrate = 38400);

ser.write("hello!".encode())

ser.close()



