from common import averagePoints

def calcRobotPath(RFCoord, RBCoord, B0Coord, B1Coord):
    grid = [[False] * 18 for i in range(18)]
    RCenterCoord = averagePoints(RFCoord, RBCoord)
