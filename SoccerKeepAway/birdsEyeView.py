"""
This module contains static functions for determining the birds eye view state variable
pseudocode from following websites was used:
https://en.wikipedia.org/w/index.php?title=Bresenham%27s_line_algorithm&gettingStartedReturn=true
http://www.cs.helsinki.fi/group/goa/mallinnus/lines/bresenh.html
"""

import agent
import kUtil, unittest
import math


def __getOctSwitchFuncts((x0,y0), (x1, y1)):
    """
    This is an internal function meant to figure out which octant that a pair of coordinates
    are using. It wil then get the input conversion function, and the output conversion
    function and return them as a tuple
    
    :param (x0,y0): coordinate 1
    :param (x1,y1): coordinate 2
    
    :type (x0,y0): a tuple of numbers
    :type (x1,y1): a tuple of numbers
    
    :returns: a tuple containing the 2 lamba functions: at index 0 is the function for converting
        from quadrant 0 to whatever quadrant the points are using. The 2nd function converts back
    
    :rtype: a tuple of lambdas
    """
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
                return (lambda (x,y): (x,y) , lambda (x,y): (x,y) )
            else:
                #oct 1
                return (lambda (x,y): (y, x) , lambda (x,y): (y, x) )
        else:
            #oct 6 or 7
            if mag < 1.0:
                #oct 7
                return ( lambda (x,y): (x, -y) , lambda(x,y): (x, -y) )
            else:
                #oct 6
                return ( lambda (x,y): (-y, x) , lambda (x,y): (y, -x) )
    else:
        #oct 2, 3, 4, or 5
        if (deltay > 0):
            #oct 2 or 3
            if mag < 1.0:
                #oct 3
                return ( lambda (x,y): (-x, y),  lambda (x,y):(-x, y) )
            else:
                #oct 2
                return ( lambda (x,y): (y, -x),  lambda (x,y): (-y, x) )
        else:
            #oct 4 or 5
            if mag < 1.0:
                #oct 4
                return ( lambda (x,y): (-x, -y) , lambda (x,y):(-x, -y) )
            else:
                #oct 5
                return ( lambda (x,y): (-y, -x), lambda (x,y): (-y, -x) )

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
    return ( math.floor(coord[0]/blocksize), math.floor(coord[1]/blocksize) )

def getBirdsEyeView(keeperArray, takerArray, display_width, display_height, block_size):
    keeperPaths = []
    takerPaths = []
    takerPositions = []
    keeperPositions = []
    sortedKeepers = sorted(keeperArray)
    keeperPositions.append(convertToTile(sortedKeepers[0].getNoisyMidPoint()))
    for i in range(1, len(keeperArray)):
        keeperPaths.append(getPathTiles(convertToTile( sortedKeepers[0].getNoisyMidPoint(), block_size), 
                     convertToTile( sortedKeepers[i].getNoisyMidPoint(), block_size) ) )
        keeperPositions.append(convertToTile(sortedKeepers[i].getNoisyMidPoint()))
        
    for i in range(len(takerArray)):
        takerPaths.append(getPathTiles(convertToTile( sortedKeepers[0].getNoisyMidPoint(), block_size), 
                     convertToTile( takerArray[i].getNoisyMidPoint(), block_size) ) )
        takerPositions.append(convertToTile(sortedKeepers[0].getNoisyMidPoint()))
    returnGrid = [] #access values as row, col
    for i in range(len(math.ceil(display_height/block_size))):
        returnGrid.append([]) 
        for j in range(len(math.ceil(display_width/block_size))):
            returnGrid.append(0.0) 
    print(returnGrid)
    
    return

def getPathTiles((x0,y0), (x1, y1)):
    #Trivial case
    if (x0,y0)== (x1, y1):
        points = [] 
        return points.append((x0,y0))
    
    #make sure that x0,y0 contains the x with the smaller value
    #you HAVE to draw the line from left to right!
    if (x0 > x1):
        temp = (x0,y0)
        (x0,y0)  = (x1,y1)
        (x1,y1) = temp
        
    converters = __getOctSwitchFuncts((x0,y0), (x1, y1))
    #convert to octant 1
    pointOne = converters[0]((x0,y0))
    pointTwo = converters[0]((x1,y1))
    
    points =  __getQuadOneTiles((x0,y0), (x1, y1))
    
    for i in range(len(points)):
        #convert all the points back to the right octant
        points[i] = converters[1](points[i])
    return points
    

#note: only tested octant 1. too tedious to test all 8
class testingCode(unittest.TestCase):
    #test octant 1
    def testGetQuadOneTiles(self):
        coords = getPathTiles( (0,1) , (6,4) )
        self.assertEqual( coords[0] , (0,1) )
        self.assertEqual( coords[1] , (1,1) )
        self.assertEqual( coords[2] , (2,2) )
        self.assertEqual( coords[3] , (3,2) )
        self.assertEqual( coords[4] , (4,3) )
        self.assertEqual( coords[5] , (5,3) )
        self.assertEqual( coords[6] , (6,4) )
    #test octant 1 with coordinates reversed 
    def testGetQuadOneTilesTwo(self):
        coords = getPathTiles( (6,4), (0,1) )
        self.assertEqual( coords[0] , (0,1) )
        self.assertEqual( coords[1] , (1,1) )
        self.assertEqual( coords[2] , (2,2) )
        self.assertEqual( coords[3] , (3,2) )
        self.assertEqual( coords[4] , (4,3) )
        self.assertEqual( coords[5] , (5,3) )
        self.assertEqual( coords[6] , (6,4) )
        
    #just make sure it won't get suck in while
    def testGetQuadOneTilesThree(self):
        #quad 1
        coords = getPathTiles( (0,1), (10,2) )
        coords = getPathTiles( (10,2), (0,1) )
        #quad 2
        coords = getPathTiles( (0,1), (-1, 10) )
        coords = getPathTiles( (-1, 10),(0,1) )
        #quad 3
        coords = getPathTiles( (0,1),(-10,2) )
        coords = getPathTiles( (-10,2),(0,1) )
        #quad 4
        coords = getPathTiles( (0,1),(-10,-1) )
        coords = getPathTiles( (-10,-1),(0,1) )
        #quad 5
        coords = getPathTiles( (0,1),(-1,-10) )
        coords = getPathTiles( (-1,-10),(0,1) )
        #quad 6
        coords = getPathTiles( (0,1),(1,-10) )
        coords = getPathTiles( (1,-10),(0,1) )
        #quad 7
        coords = getPathTiles( (1,0),(10,-1) )
        coords = getPathTiles( (10,-1),(1,0) )
    
    def testGetQuadOneTilesFour(self):
        #extreme test cases
        coords = getPathTiles( (0,0),(0,0) )
        coords = getPathTiles( (0,0),(0,1) )
        coords = getPathTiles( (0,0),(1,0) )
        coords = getPathTiles( (0,0),(0,-1) )
        coords = getPathTiles( (0,0),(-1,0) )
        
if __name__ == "__main__":
    print('Unit Testing') 
    unittest.main()
