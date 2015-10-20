"""
This module contains a static functions for determining the birds eye view state variable
pseudocode from following websites was used:
https://en.wikipedia.org/w/index.php?title=Bresenham%27s_line_algorithm&gettingStartedReturn=true
http://www.cs.helsinki.fi/group/goa/mallinnus/lines/bresenh.html

The only function that should be called from here by the simulator class is getBirdsEyeView
"""

import agent
import kUtil, unittest
import math

lambdaDict = {}

lambdaDict[0] = (lambda (x,y): (x,y) , lambda (x,y): (x,y) )
lambdaDict[1] = (lambda (x,y): (y, x) , lambda (x,y): (y, x) )
lambdaDict[2] = ( lambda (x,y): (y, -x),  lambda (x,y): (-y, x) )
lambdaDict[3] = ( lambda (x,y): (-x, y),  lambda (x,y):(-x, y) )
lambdaDict[4] = ( lambda (x,y): (-x, -y) , lambda (x,y):(-x, -y) )
lambdaDict[5] = ( lambda (x,y): (-y, -x), lambda (x,y): (-y, -x) )
lambdaDict[6] = ( lambda (x,y): (-y, x) , lambda (x,y): (y, -x) )
lambdaDict[7] = ( lambda (x,y): (x, -y) , lambda(x,y): (x, -y) )



def getOctant((x0,y0), (x1, y1)):
    # +x , +y, oct 0 or 1
    # -x , +y, oct 2 or 3
    # -x , -y, oct 4 or 5
    # +x , -y, oct 6 or 7
    #abs(slope) < 1 means even oct
    #abs(slop)  > 1 means odd oct
    deltax = x1 - x0
    deltay = y1 - y0
    if deltax != 0:
        mag = abs(float(deltay) / float(deltax))
    else:
        mag = float("Inf")
    if (deltax > 0):
        #oct 0, 1, 6, or 7
        if (deltay > 0):
            #oct 0 or 1
            if mag < 1.0:
                #oct 0
                return 0
            else:
                #oct 1
                return 1
        else:
            #oct 6 or 7
            if mag < 1.0:
                #oct 7
                return 7
            else:
                #oct 6
                return 6
    else:
        #oct 2, 3, 4, or 5
        if (deltay > 0):
            #oct 2 or 3
            if mag < 1.0:
                #oct 3
                return 3
            else:
                #oct 2
                return 2
        else:
            #oct 4 or 5
            if mag < 1.0:
                #oct 4
                return 4
            else:
                #oct 5
                return 5

def getLambdasas((x0,y0), (x1, y1)):       
    return lambdaDict[getOctant((x0, y0), (x1, y1))]         

def __getQuadOneTiles((x0,y0), (x1, y1)):       
    dx = x1 - x0
    dy = y1 - y0
    
    D = 2 * dy - dx
    returnList = []
    returnList.append( (x0, y0) )
    y = y0
    x = x0 + 1
    while x != x1 + 1:
        returnList.append( (x,y) )
        D = D + (2*dy)
        #print("D is now ", D)
        if D > 0:
            y = y + 1
            D = D - (2 * dx)
        #original return list appending
        #returnList.append( (x,y) )
        x = x + 1
    #print returnList
    return returnList


#getBirdsEyeView(self.keeperArray, self.takerArray, self.__display_width, self.display_height, self.__agent_block_size)
def convertToTile(coord, blocksize):
    #print("orig coord: ", coord)
    #print("new tile: ", ( math.floor(coord[0]/blocksize), math.floor(coord[1]/blocksize) ))
    return ( math.floor(coord[0]/blocksize), math.floor(coord[1]/blocksize) )

def getBirdsEyeView(keeperArray, takerArray, display_width, display_height, block_size):
    """
    This function will take in the array of keepers, takers, the display width of the simulator, 
    the display height of the simulator, and the block size that you want to make the tiles. Note:
    I currently only support a block size of 23 pixels by 23 pixels
    
    .. note::
        This is the ONLY function from the birdEyeView.py module that should be called by the 
        simulator. All other functions in this modules are private functions, but are left
        callable simply in order to unit test in the development phase of this module
    
    :param keeperArray: The array of all keepers
    :param takerArray: the array of all takers
    :param display_width: the width of the simulator field in pixels
    :param display_height: the height of the simuator field in pixels
    :param block_size: the side length of the square tiles that will form the birds eye view
    
    :type keeperArray: an array of keepers, each keeper being of type agent (or a subclass of agent)
    :type takerArray: an array of takers, each taker being of type agent (or a subclass of agent)
    :type display_width: an integer
    :type display_height: an integer
    :type block_size: an integer
    
    :returns: the birds eye view of the whole field
    :rtype: a list of a list of doubles
    
    """
    keeperPaths = []
    takerPaths = []
    takerPositions = []
    keeperPositions = []
    sortedKeepers = sorted(keeperArray)
    keeperPositions.append(convertToTile(sortedKeepers[0].getNoisyMidPoint(), block_size))
    for i in range(1, len(keeperArray)):
        keeperPaths.append(getPathTiles((convertToTile( sortedKeepers[0].getNoisyMidPoint(), block_size), 
                     convertToTile( sortedKeepers[i].getNoisyMidPoint(), block_size) ) ) )
        keeperPositions.append(convertToTile(sortedKeepers[i].getNoisyMidPoint(), block_size))
        
    for i in range(len(takerArray)):
        takerPaths.append(getPathTiles((convertToTile( sortedKeepers[0].getNoisyMidPoint(), block_size), 
                     convertToTile( takerArray[i].getNoisyMidPoint(), block_size) ) ) )
        takerPositions.append(convertToTile(takerArray[i].getNoisyMidPoint(), block_size))
    returnGrid = [] #access values as row, col
    for i in range(int(math.ceil(display_height/block_size))):
        returnGrid.append([]) 
        for j in range(int(math.ceil(display_width/block_size))):
            returnGrid[i].append(0.0) 
            
    for path in takerPaths:
        for tile in path:
            returnGrid[int(tile[0])][int(tile[1])] += -0.3
    for path in keeperPaths:
        for tile in path:
            returnGrid[int(tile[0])][int(tile[1])] += 0.3
    
    for tile in keeperPositions:
        returnGrid[int(tile[0])][int(tile[1])] = 1.0
    for tile in takerPositions:
        returnGrid[int(tile[0])][int(tile[1])] = -1.0
    
    return returnGrid


def getPathTiles(pointsPair):
    #Trivial case
    if pointsPair[0]== pointsPair[1]:
        points = [] 
        return points.append(pointsPair[0])
    
    """
    #make sure that x0,y0 contains the x with the smaller value
    #you HAVE to draw the line from left to right!
    if (x0 > x1):
        temp = (x0,y0)
        (x0,y0)  = (x1,y1)
        (x1,y1) = temp
    """
        
    converters = getLambdasas(pointsPair[0], pointsPair[1])
    #convert to octant 1
    newPointsPair = []
    for i in range(len(pointsPair)):
        newPointsPair.append(getLambdasas( pointsPair[0], pointsPair[1] )[0](pointsPair[i]))

    points =  __getQuadOneTiles(newPointsPair[0], newPointsPair[1])
    
    for i in range(len(points)):
        #convert all the points back to the right octant
        points[i] = converters[1](points[i])
    return points
    

#note: only tested octant 1. too tedious to test all 8
class testingCode(unittest.TestCase):
    #test to see if you are detecting octants correctly
    def testOctTest(self):
        #oct 0
        print(getOctant( (0,1), (10,2) ) )
        self.assertEquals( getOctant( (0,1), (10,2) ), 0)
        #oct 1
        print(getOctant( (0,1), (1, 10) ) )
        self.assertEquals( getOctant( (0,1), (1, 10) ), 1)
        #oct 2
        print(getOctant( (0,1), (-1, 10) ) )
        self.assertEquals( getOctant( (0,1), (-1, 10) ), 2)
        #oct 3
        print(getOctant( (0,1), (-10, 2) ) )
        self.assertEquals( getOctant( (0,1), (-10, 2) ), 3)
        #oct 4
        print(getOctant( (10,2), (0,1) ) )
        self.assertEquals( getOctant( (10,2), (0,1) ), 4)
        #oct 5
        print(getOctant( (1, 10),(0,1) ) )
        self.assertEquals( getOctant( (1, 10),(0,1) ), 5)
        #oct 6
        print(getOctant( (-1, 10), (0,1) ) )
        self.assertEquals( getOctant( (-1, 10), (0,1) ), 6)
        #oct 7
        print(getOctant( (-10, 2), (0,1) ) )
        self.assertEquals( getOctant( (-10, 2), (0,1) ), 7)
    
    #test to make sure that the octants are being converted 
    #to octant 1 correctly
    def testConversions(self):
        #oct 0
        points = (0,1), (10,2)
        print(getOctant( points[0], points[1] ) )
        newPoint = getLambdasas( points[0], points[1] )[0](points)
        self.assertEquals( getOctant(newPoint[0],  newPoint[1]), 0)
        
        #oct 1
        points = (0,1), (1, 10)
        print ("orig", points)
        print(getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( getOctant(newPoint[0],  newPoint[1]), 0)

        #oct 2
        points = (0,1), (-1, 10)
        print ("orig", points)
        print(getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 3
        points = (0,1), (-10, 2)
        print ("orig", points)
        print(getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 4
        points = (10,2), (0,1)
        print ("orig", points)
        print(getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 5
        points = (1, 10),(0,1) 
        print ("orig", points)
        print(getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 6
        points = (-1, 10), (0,1)
        print ("orig", points)
        print(getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 7
        points = (-10, 2), (0,1)
        print ("orig", points)
        print(getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( getOctant(newPoint[0],  newPoint[1]), 0)

        
    #test octant 0
    def testGetOctOneTiles(self):
        coords = getPathTiles( ((0,1) , (6,4)) )
        self.assertEqual( coords[0] , (0,1) )
        self.assertEqual( coords[1] , (1,1) )
        self.assertEqual( coords[2] , (2,2) )
        self.assertEqual( coords[3] , (3,2) )
        self.assertEqual( coords[4] , (4,3) )
        self.assertEqual( coords[5] , (5,3) )
        self.assertEqual( coords[6] , (6,4) )


    def testGetQuadOneTilesFour(self):
        #extreme test cases
        coords = getPathTiles( ((0,0),(0,0)) )
        coords = getPathTiles( ((0,0),(0,1)) )
        coords = getPathTiles( ((0,0),(1,0)) )
        coords = getPathTiles( ((0,0),(0,-1)) )
        coords = getPathTiles( ((0,0),(-1,0)) )

if __name__ == "__main__":
    print('Unit Testing') 
    unittest.main()
