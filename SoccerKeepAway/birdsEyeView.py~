"""
This module contains a static functions for determining the birds eye view state variable.

pseudocode from following website was used:
https://en.wikipedia.org/w/index.php?title=Bresenham%27s_line_algorithm&gettingStartedReturn=true

The only function that should be called from here by the simulator class is "getBirdsEyeView()".
No other functions are documented as they are simply private functions to help the main 
function "getBirdsEyeView()"
"""
import unittest
import math
class birdsEyeView():
    """
    The birdsEyeView Class. After this class is initialized by the simulator, the simulator can call 
    the getBirdsEyeView function, which will return a grid containing the birdsEyeView. The simulator
    will then send this birdsEyeView to any agent that requests it. 
    """
    def __init__(self, block_size = 23, ball_size = 12):
        self.__block_size = block_size
        self.__ball_size = ball_size
        self.lambdaDict = {}
        self.lambdaDict[0] = (lambda point: (point[0],point[1]) , lambda point: (point[0],point[1]) )
        self.lambdaDict[1] = (lambda point: (point[1], point[0]) , lambda point: (point[1], point[0]) )
        self.lambdaDict[2] = ( lambda point: (point[1], -point[0]),  lambda point: (-point[1], point[0]) )
        self.lambdaDict[3] = ( lambda point: (-point[0], point[1]),  lambda point:(-point[0], point[1]) )
        self.lambdaDict[4] = ( lambda point: (-point[0], -point[1]) , lambda point:(-point[0], -point[1]) )
        self.lambdaDict[5] = ( lambda point: (-point[1], -point[0]), lambda point: (-point[1], -point[0]) )
        self.lambdaDict[6] = ( lambda point: (-point[1], point[0]) , lambda point: (point[1], -point[0]) )
        self.lambdaDict[7] = ( lambda point: (point[0], -point[1]) , lambda point: (point[0], -point[1]) )

    
    def getAgentBlockSize(self):
        """
        Get the length/height of the square tiles used here
        
        :returns: the tile height/width for a tile on the birdseye view
        
        :rtype: integer
        """
        return self.__block_size
    
    def getBallSize(self):
        """
        Get the length/height of the square tile that represents the ball. While the ball tile is never used
        in the birdseye view, it's useful to have this function for other class that require both a birdeyeview,
        and would need the block size of the ball to determine where the center of the ball is.
        
        :returns: the tile height/width of the ball
        
        :rtype: integer
        """
        return self.__ball_size

    def getOctant(self, pointOne, pointTwo):
        (x0,y0) = pointOne
        (x1, y1) = pointTwo
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
    
    def getLambdasas(self, pointOne, pointTwo):
        (x0,y0) = pointOne      
        (x1, y1) = pointTwo 
        return self.lambdaDict[self.getOctant((x0, y0), (x1, y1))]         
    
    def __getQuadOneTiles(self, pointOne, pointTwo):       
        (x0,y0) = pointOne
        (x1, y1) = pointTwo
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
    def __convertToTile(self, coord):
        #print("orig coord: ", coord)
        #print("new tile: ", ( math.floor(coord[0]/blocksize), math.floor(coord[1]/blocksize) ))
        return ( math.floor(coord[0]/self.__block_size), math.floor(coord[1]/self.__block_size) )
    
    def getBirdsEyeViewAsList(self, keeperArray, takerArray, display_width, display_height):
        grid = self.getBirdsEyeView(keeperArray, takerArray, display_width, display_height)
        returnlist = []
        for l in grid:
            returnlist = returnlist + l
        return returnlist
    
    def getSubstrate(self, keeperArray, takerArray, display_width, display_height):
        grid = self.getBirdsEyeView(keeperArray, takerArray, display_width, display_height)
        for i in range(len(grid)):
            #i iterates over rows
            for j in range(len(grid[i])):
                #j iterates over columns
                grid[i][j] = (i * self.getAgentBlockSize() + (self.getAgentBlockSize()/2),
                              j* self.getAgentBlockSize() + (self.getAgentBlockSize()/2))
        returnList = []
        for l in grid:
            returnList = returnList + l
        return returnList
        
    
    def getBirdsEyeView(self, keeperArray, takerArray, display_width, display_height):
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
        
        :type keeperArray: an array of keepers, each keeper being of type agent (or a subclass of agent)
        :type takerArray: an array of takers, each taker being of type agent (or a subclass of agent)
        :type display_width: an integer
        :type display_height: an integer
        
        :returns: the birds eye view of the whole field
        :rtype: a list of a list of doubles
        """
        keeperPaths = []
        takerPaths = []
        takerPositions = []
        keeperPositions = []
        sortedKeepers = sorted(keeperArray)
        keeperPositions.append(self.__convertToTile(sortedKeepers[0].getNoisyMidPoint()))
        for i in range(1, len(keeperArray)):
            keeperPaths.append(self.getPathTiles((self.__convertToTile( sortedKeepers[0].getNoisyMidPoint()), 
                         self.__convertToTile( sortedKeepers[i].getNoisyMidPoint()) ) ) )
            keeperPositions.append(self.__convertToTile(sortedKeepers[i].getNoisyMidPoint()))
            
        for i in range(len(takerArray)):
            takerPaths.append(self.getPathTiles((self.__convertToTile( sortedKeepers[0].getNoisyMidPoint()), 
                         self.__convertToTile( takerArray[i].getNoisyMidPoint()) ) ) )
            takerPositions.append(self.__convertToTile(takerArray[i].getNoisyMidPoint()))
        returnGrid = [] #access values as row, col
        for i in range(int(math.ceil(display_height/self.__block_size))):
            returnGrid.append([]) 
            for j in range(int(math.ceil(display_width/self.__block_size)) ):
                returnGrid[i].append(0.0) 
                
        for path in takerPaths:
			if path != None:
				for tile in path:
					returnGrid[int(tile[0])][int(tile[1])] += -0.3
        for path in keeperPaths:
			if path != None:
				for tile in path:
					returnGrid[int(tile[0])][int(tile[1])] += 0.3
        
        for i in range(len(keeperPositions)):
            if i != 0: 
                returnGrid[int(keeperPositions[i][0])][int(keeperPositions[i][1])] = 1.0
            else:
                returnGrid[int(keeperPositions[i][0])][int(keeperPositions[i][1])] = 1.1
        for tile in takerPositions:
            returnGrid[int(tile[0])][int(tile[1])] = -1.0
        
        return returnGrid
    
    
    def getPathTiles(self, pointsPair):
        #Trivial case
        if pointsPair[0]== pointsPair[1]:
            points = [] 
            return points.append(pointsPair[0])            
        converters = self.getLambdasas(pointsPair[0], pointsPair[1])
        #convert to octant 1
        newPointsPair = []
        for i in range(len(pointsPair)):
            newPointsPair.append(self.getLambdasas( pointsPair[0], pointsPair[1] )[0](pointsPair[i]))
    
        points =  self.__getQuadOneTiles(newPointsPair[0], newPointsPair[1])
        
        for i in range(len(points)):
            #convert all the points back to the right octant
            points[i] = converters[1](points[i])
        return points

        

#note: only tested octant 1. too tedious to test all 8
class testingCode(unittest.TestCase):
    
    def testGetGridAsList(self):
        import keepAway
        world = keepAway.keepAway(0)
        e = birdsEyeView()
        grid = e.getBirdsEyeView(world.keeperArray, world.takerArray, world.get_display_width(), world.get_display_height())
        listGrid = e.getBirdsEyeViewAsList(world.keeperArray, world.takerArray, world.get_display_width(), world.get_display_height())
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                self.assertEqual(grid[i][j], listGrid[i * len(grid[i]) + j])
                
        
        
    
    #test to see if you are detecting octants correctly
    def testOctTest(self):
        #oct 0
        e = birdsEyeView()
        print(e.getOctant( (0,1), (10,2) ) )
        self.assertEquals( e.getOctant( (0,1), (10,2) ), 0)
        #oct 1
        print(e.getOctant( (0,1), (1, 10) ) )
        self.assertEquals( e.getOctant( (0,1), (1, 10) ), 1)
        #oct 2
        print(e.getOctant( (0,1), (-1, 10) ) )
        self.assertEquals( e.getOctant( (0,1), (-1, 10) ), 2)
        #oct 3
        print(e.getOctant( (0,1), (-10, 2) ) )
        self.assertEquals( e.getOctant( (0,1), (-10, 2) ), 3)
        #oct 4
        print(e.getOctant( (10,2), (0,1) ) )
        self.assertEquals( e.getOctant( (10,2), (0,1) ), 4)
        #oct 5
        print(e.getOctant( (1, 10),(0,1) ) )
        self.assertEquals( e.getOctant( (1, 10),(0,1) ), 5)
        #oct 6
        print(e.getOctant( (-1, 10), (0,1) ) )
        self.assertEquals( e.getOctant( (-1, 10), (0,1) ), 6)
        #oct 7
        print(e.getOctant( (-10, 2), (0,1) ) )
        self.assertEquals( e.getOctant( (-10, 2), (0,1) ), 7)
    
    #test to make sure that the octants are being converted 
    #to octant 1 correctly
    def testConvertToOctOne(self):
        e = birdsEyeView()
        #oct 0
        points = (0,1), (10,2)
        print(e.getOctant( points[0], points[1] ) )
        newPoint = e.getLambdasas( points[0], points[1] )[0](points)
        self.assertEquals( e.getOctant(newPoint[0],  newPoint[1]), 0)
        
        #oct 1
        points = (0,1), (1, 10)
        print ("orig", points)
        print(e.getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(e.getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( e.getOctant(newPoint[0],  newPoint[1]), 0)

        #oct 2
        points = (0,1), (-1, 10)
        print ("orig", points)
        print(e.getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(e.getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( e.getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 3
        points = (0,1), (-10, 2)
        print ("orig", points)
        print(e.getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(e.getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( e.getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 4
        points = (10,2), (0,1)
        print ("orig", points)
        print(e.getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(e.getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( e.getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 5
        points = (1, 10),(0,1) 
        print ("orig", points)
        print(e.getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(e.getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( e.getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 6
        points = (-1, 10), (0,1)
        print ("orig", points)
        print(e.getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(e.getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( e.getOctant(newPoint[0],  newPoint[1]), 0)
        #oct 7
        points = (-10, 2), (0,1)
        print ("orig", points)
        print(e.getOctant( points[0], points[1] ) )
        newPoint = []
        for i in range(len(points)):
            newPoint.append(e.getLambdasas( points[0], points[1] )[0](points[i]))
        print ("new", newPoint)
        self.assertEquals( e.getOctant(newPoint[0],  newPoint[1]), 0)

        
    #test octant 0
    def testGetOctOneTiles(self):
        e = birdsEyeView()
        coords = e.getPathTiles( ((0,1) , (6,4)) )
        self.assertEqual( coords[0] , (0,1) )
        self.assertEqual( coords[1] , (1,1) )
        self.assertEqual( coords[2] , (2,2) )
        self.assertEqual( coords[3] , (3,2) )
        self.assertEqual( coords[4] , (4,3) )
        self.assertEqual( coords[5] , (5,3) )
        self.assertEqual( coords[6] , (6,4) )


    def testGetQuadOneTilesFour(self):
        #extreme test cases
        e = birdsEyeView()
        e.getPathTiles( ((0,0),(0,0)) )
        e.getPathTiles( ((0,0),(0,1)) )
        e.getPathTiles( ((0,0),(1,0)) )
        e.getPathTiles( ((0,0),(0,-1)) )
        e.getPathTiles( ((0,0),(-1,0)) )

if __name__ == "__main__":
    print('Unit Testing') 
    unittest.main()
