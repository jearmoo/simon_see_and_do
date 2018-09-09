from common import *
from constants import *
import math

def pointToRoundTuple(point):
    x,y = point
    return (round(x),round(y))

def init_queue():
    return []

def enqueue(queue,x):
    queue.append(x)

def dequeue(queue):
    return queue.pop(0)

def calcRobotPath(RFCoordInches, RBCoordInches, B0CoordInches, B1CoordInches, blockMoved):
    
    RCenterCoord = averagePoints([RFCoordInches, RBCoordInches])

    robotMinCoord = Point(RCenterCoord.x - ROBOT_TOLERANCE, RCenterCoord.y - ROBOT_TOLERANCE)
    robotMaxCoord = Point(RCenterCoord.x + ROBOT_TOLERANCE, RCenterCoord.y + ROBOT_TOLERANCE)

    obstacleCoord = B1CoordInches if (blockMoved[0] == B0_ID) else B0CoordInches
    obstacleMinCoord = Point(math.floor(obstacleCoord.x - BLOCK_TOLERANCE), math.ceil(obstacleCoord.y - ROBOT_TOLERANCE))
    obstacleMaxCoord = Point(math.floor(obstacleCoord.x + BLOCK_TOLERANCE), math.ceil(obstacleCoord.y + ROBOT_TOLERANCE))

    def fillObstacle(grid):
        for i in range(max(obstacleMinCoord.y, 0), min(obstacleMaxCoord.y + 1, ARENA_HEIGHT)):
            for j in range(max(obstacleMinCoord.x, 0), min(obstacleMaxCoord.x + 1, ARENA_WIDTH)):
                grid[i][j] = False


    # If match One Dim, then BFS will search until one dimension is matched
    def BFS(start, end, matchOneDim=False):
        # true means it's available
        grid = []
        for i in range(ARENA_HEIGHT):
            row = []
            for j in range(ARENA_WIDTH):
                row.append((1 < i < 16) or (1 < j < 16))

            grid.append(row) 

        print(grid)
        grid[start[1]][start[0]] = False



        fillObstacle(grid)

        queue = init_queue()
        parentDict = {}

        # 0 is left
        # 1 is right
        # 2 is up
        # 3 is down
        # prevDirection is the direction taken to get to the current node
        def unvisited_neighbors(point, prevDirection):
            x,y = point
            # [left, right, down, up]
            neighbors = [None,None,None,None]
            if x-1 >= 0 and grid[y][x-1]:
                neighbors[0] = ((x-1, y),0)
                grid[y][x-1] = False
            if x+1 < ARENA_WIDTH and grid[y][x+1]:
                neighbors[1] = ((x+1, y),1)
                grid[y][x+1] = False
            if y-1 >= 0 and grid[y-1][x]:
                neighbors[2] = ((x, y-1),2)
                grid[y-1][x] = False
            if y+1 < ARENA_HEIGHT and grid[y+1][x]:
                neighbors[3] = ((x, y+1),3)
                grid[y+1][x] = False

            result = []

            # append the previous direction move first
            if prevDirection != None and neighbors[prevDirection] != None:
                result.append(neighbors[prevDirection])
                neighbors[prevDirection] = None

            # append the rest
            for n in neighbors:
                if n != None:
                    result.append(n)

            return result

        enqueue(queue, (start, None))
        while queue != []:
            node, prevDirection = dequeue(queue)

            # complete match
            if not(matchOneDim) and (node[0] == end[0] and node[1] == end[1]):
                endNode = node
                break

            # x or y matches with the end
            if matchOneDim and (node[0] == end[0] or node[1] == end[1]):
                endNode = node
                break

            neighbors = unvisited_neighbors(node,prevDirection)

            for n, prevD in neighbors:
                enqueue(queue,(n,prevD))
                parentDict[n] = node


        # print(parentDict)

        path = []
        current = endNode

        while current != start:
            # print(current)
            path.append(current)
            current = parentDict[current]

        path.append(start)

        return list(reversed(path))

    def calcPath(start,end):
        # first calculate path from rcenter to blockMoved[0] position
        # Calculate path to one dim, then two dim, to minimize turning
        # TODO: for now rounding both point dimensions. improve it laster
        roundedStart = pointToRoundTuple(start)

        
        roundedEnd = pointToRoundTuple(end)

        
        pathFirstHalf = BFS(roundedStart,roundedEnd, True)
        lastPoint = pathFirstHalf[-1]
        if lastPoint == roundedEnd:
            path = pathFirstHalf
        else:
            pathFirstHalf.pop(-1)
            print(lastPoint, roundedEnd)
            path = pathFirstHalf + BFS(lastPoint, roundedEnd)

        return path

    goalBlock = B0CoordInches if blockMoved[0] == B0_ID else B1CoordInches
    
    firstPath = calcPath(RCenterCoord, goalBlock)

    secondPath = calcPath(goalBlock, blockMoved[1])

    return firstPath + ["pickup"] + secondPath + ["drop"]


testRobotPos = Point(13,13)
testB0 = Point(8,13)
testB1 = Point(0,13)
testBlockMoved = ("b1",(4,13))
testPath = calcRobotPath(testRobotPos, testRobotPos, testB0, testB1, testBlockMoved)
print(testPath)
