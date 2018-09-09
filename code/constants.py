import math

#SEE_URL ='http://10.251.82.37:8080/shot.jpg'
GO_URL ='http://10.251.82.37:8080/shot.jpg'
SEE_URL = 'http://10.251.79.113:8080/shot.jpg'

SEE_SOCKET_ADDRESS = "/tmp/see_socket"
GO_SOCKET_ADDRESS = "/tmp/go_socket"

SEE_WIDTH = 1440
SEE_HEIGHT = 1080

DO_WIDTH = 1280
DO_HEIGHT = 960

FRAME_DELAY_MS = 100

ESCAPE_KEY = 27

QRCODE_TO_INDEX_MAP = {"b0": 0, "b1": 1, "c0": 2, "c1": 3}

# boxes
B0_ID = "b0"
B1_ID = "b1"
# corners
C0_ID = "c0"
C1_ID = "c1"
# simon (robot front and robot back)
RF_ID = "rf"
RB_ID = "rb"

STABLE_EPSILON = 20

ARENA_HEIGHT = 18
ARENA_WIDTH = 18

# must be greater than 2
MOVING_N = 5

ROBOT_TOLERANCE = 2.5
BLOCK_TOLERANCE = 2

ROBOT_PORT = "/dev/cu.H-C-2010-06-01-DevB"
LED_PORT = "/dev/cu.SLAB_USBtoUART"

COMMAND_ROBOT = True

ROTATION_TOLERANCE_DEGREES = 4
ROTATION_TOLERANCE = math.radians(ROTATION_TOLERANCE_DEGREES)

CALIBRATE_ROTATION = True

FINAL_REDUCTION_TENTH_INCHES = 45