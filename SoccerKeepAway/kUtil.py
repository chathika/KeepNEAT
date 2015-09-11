import unittest
import math
import random

#This is a custom made util file for keepaway

#UNIT TESTED
#input: 2 vectors or coordinates, a and b
#output: true if the dimensions are the same, false otherwise
def doDimMatch(a, b):
    if len(a) != len(b):
        print("dimensions do not match")
        return False
    return True

#UNIT TESTED
#input: take in a pair of 2D cartesian points, a and b
#output: the vector from a to b
def getVector(a, b):
    if doDimMatch(a,b):
        return (b[0] - a[0], b[1] - a[1])

#UNIT TESTED
#get the squared distance between 2 points.
#useful if all you're doing is trying to find max
#or min distance, so you don't have to waste time
#doing a square root operation
def getSqrDist(a, b):
    if doDimMatch(a, b):
        vector =getVector(a, b)
        total = 0.0
        for i in range(len(vector)):
            total += vector[i] * vector[i]
        return total
    else:
        print("error, dimensions don't match for getSqrDist(", a, ",", b, ")")


#UNIT TESTED
#input: a vector
#output: a floating point magnitude of the vector
def magnitude(vector):
    total = 0.0
    for i in range(len(vector)):
        total += vector[i] * vector[i]
    return math.sqrt(total)

#UNIT TESTED
#input: 3 points, A, B, and C.
#output, cos(theta), where theta is the angle formed by ABC
#note: this function WILL calculate the sign correctly
def cosTheta (a, b, c):
    V1 = getVector(b, a)
    V2 = getVector(b,c)
    V1mag = magnitude(V1)
    V2mag = magnitude(V2)
    if(V1mag * V2mag != 0.0):
        return (V1[0] * V2[0] + V1[1] * V2[1]) / (V1mag * V2mag)
    else:
        return 0.0;

#UNIT TESTED
#input: 3 points, A, B, and C.
#output, sin(theta), where theta is the angle formed by ABC
#note: this function will always return a positive value for sin
def posSinTheta(a, b, c):
    tempCos = cosTheta(a,b,c)
    return math.sqrt(1.0 - (tempCos * tempCos))

#input: 2 points, a and b. 
#return the distance
def getDist(a,b):
        return math.sqrt(getSqrDist(a,b))
        
#UNIT TESTED
#input: take in a point and a vector
#output: go and add the vector to the point to get the new point, and return it       
def addVectorToPoint(a, vector):
    if doDimMatch(a, vector):
        returnList = [i for i in a]
        for i in range(len(a)):
            returnList[i] += vector[i]
        return tuple(i for i in returnList)

#UNIT TESTED
#input: a vector of any length besides 0
#output: the corresponding unit vector of length 1
#if a vector of 0 is put in, then 0,0 will be returned
def unitVector(vector):
    mag = magnitude(vector)
    returnList = []
    if mag == 0.0:
        for i in range(len(vector)):
            returnList.append(0.0)
    else:
        for i in range(len(vector)):
            returnList.append(vector[i] / mag)
    return tuple(i for i in returnList)

#UNIT TESTED with 2 examples
#input: 3 points, a, b, c. A
    #A is the point that you're ball is heading towards. It is the ball coord + ball Velocity
    #B is the angle vertex, which are the coordinates of the ball
    #C is the coordinates of the player, who's perpendicular position you're trying to find
#output: if you draw a line from b to a, then what is the perpendicular 
#    distance from c to that vector? that is what is returned
def getPerpDist(a, b, c):
    #the hypotenuse is from B, the vertex, to the point you're trying to find the perpendicular distance to, C. 
    hypotenuse = getDist(b, c) 
    # the hypotenuse times the sin(theta), where theta is the angle formed by ABC, will give you perpendicular distance
    return posSinTheta(a, b, c) * hypotenuse

#UNIT TESTED with 2 examples
#input: 3 points, a, b, c. A
    #A is the point that you're ball is heading towards. It is the ball coord + ball Velocity
    #B is the angle vertex, which are the coordinates of the ball
    #C is the coordinates of the player, who's perpendicular position you're trying to find
#output: if you draw a line from b to a, then what is the perpendicular vector from c to intersection point?
#    that vector is what this function returns. 
def getNormalVector(a,b,c):
    #ball travels from B to A
    #player is at point C
    cutoffDist = getPerpDist(a,b,c)
    tempVector = unitVector(getVector(b,a))
    normalVectors = []
    minDist = 9999999999.0
    #these are the normal unit vectors, times the cutoff.
    normalVectors.append((-1.0 * tempVector[1] * cutoffDist, tempVector[0]* cutoffDist))
    normalVectors.append((tempVector[1]* cutoffDist, -1.0 * tempVector[0]* cutoffDist))
    for i in range(len(normalVectors)):
        tempDistance = getDist(a, addVectorToPoint(c, normalVectors[i]))
        if  tempDistance < minDist:
            minDist = tempDistance
            returnIndex = i
    return normalVectors[returnIndex]

#NOT UNIT TESTED, but it has been tested in idle and seems to work
#input: any vector or position
#output: the noisy version of that vector or position, as sampled from a gaussian normal distribution
def getNoisyVals(vector, sigma):
    returnList = []
    for i in range(len(vector)):
        returnList.append(random.gauss(vector[i], sigma))
    return tuple(i for i in returnList)

#UNIT TESTED
#input: 2 positions a and b
#output: the midpoint between those 2 points
def getMidPoint(a,b):
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)

#input: a scalar value and a vector.
#output: scaled vector. Useful for movement functions in keepaway.py
def scalarMultiply(scalar, vector):
    returnList = []
    for i in range(len(vector)):
        returnList.append(vector[i] * scalar)
    return tuple(i for i in returnList)
            

class testingCode(unittest.TestCase):
    def test_get_vector(self):
        self.assertEqual(getVector((0.0,0.0), (1.0,1.0)), (1.0, 1.0))
        self.assertEqual(getVector((0.0,0.0), (-1.0,-1.0)), (-1.0, -1.0))
        self.assertEqual(getVector((0.5,0.5), (1.0,-1.0)), (0.5, -1.5))
        self.assertEqual(getVector((0.5,0.4), (-1.0,1.0)), (-1.5, 0.6))
        #self.assertFalse(getVector((0.0,0.0, 0.0), (-1.0,-1.0)), (-1.0, -1.0))
    def test_magnitude(self):
        self.assertEqual(magnitude((1,1)), math.sqrt(2.0))
        self.assertEqual(magnitude((-5, 10)), math.sqrt(125.0))
        self.assertEqual(magnitude((-5, -7)), math.sqrt(74.0))
        self.assertEqual(magnitude((5, -10)), math.sqrt(125.0))
    def testCosTheta(self):
        self.assertAlmostEqual(cosTheta((1,0), (0,0), (1,1)), math.cos(math.pi / 4.0))
        self.assertAlmostEqual(cosTheta((1,0), (0,0), (1,-1)), math.cos(-1.0 *math.pi / 4.0))
        self.assertAlmostEqual(cosTheta((1,0), (0,0), (-1,1)), math.cos(3.0 * math.pi / 4.0))
        self.assertAlmostEqual(cosTheta((1,0), (0,0), (-1,-1)), math.cos(-3.0 * math.pi / 4.0))
        self.assertAlmostEqual(cosTheta((1,0), (0,0), (1,0)), 1.0)
        self.assertAlmostEqual(cosTheta((1,0), (0,0), (0,1)), 0.0)
        self.assertAlmostEqual(cosTheta((1,0), (0,0), (-1,0)), -1.0)
        self.assertAlmostEqual(cosTheta((1,0), (0,0), (math.sqrt(3.0)/ 2.0 , 0.5)), math.cos(1.0/6.0 * math.pi ))
    def testPosSinTheta(self):
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (1,1)), abs(math.sin(math.pi / 4.0)))
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (1,-1)), abs(math.sin(-1.0 *math.pi / 4.0)))
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (-1,1)), abs(math.sin(3.0 * math.pi / 4.0)))
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (-1,-1)), abs(math.sin(-3.0 * math.pi / 4.0)))
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (1,0)), 0.0)
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (0,1)), 1.0)
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (0,-1)), 1.0)
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (-1,0)), 0.0)
        self.assertAlmostEqual(posSinTheta((1,0), (0,0), (math.sqrt(3.0)/ 2.0, 0.5 )), abs(math.sin(1.0/6.0 * math.pi )))
    def testAddVectorToPoint(self):
        self.assertAlmostEqual(addVectorToPoint((.5, .4), (15, 30)), (15.5, 30.4))
        self.assertAlmostEqual(addVectorToPoint((.5, -.4), (-15, 30)), (-14.5, 29.6))
    def testUnitVector(self):
        v = (15.0, -17.0)
        uv = unitVector(v)
        mag = magnitude(v)
        self.assertAlmostEqual(v[0] / mag, uv[0])
        self.assertAlmostEqual(v[1] / mag, uv[1])
        v = (0,0)
        uv = unitVector(v)
        self.assertEqual(uv, (0,0))
    def testGetPerpDist(self):
        a = (6,-3)
        b = (0,0)
        c = (4,0)
        dist = getPerpDist(a, b, c)
        self.assertAlmostEqual(dist, math.sqrt(3.2))
        a = (2,3)
        b = (0,0)
        c = (1,-5)
        dist = getPerpDist(a, b, c)
        self.assertAlmostEqual(dist, math.sqrt(13)) 
        
    def getSqrDist(self):
        a = (-1, 1)
        b = (5, 10)
        sqrDist = getSqrDist(a, b)
        self.assertEqual(sqrDist, 117)

    def testGetNormalVector(self):
        a = (6,-3)
        b = (0,0)
        c = (4,0)
        vector = getNormalVector(a, b, c)
        self.assertAlmostEqual(vector[0], -.8)
        self.assertAlmostEqual(vector[1],-1.6)
        a = (2,3)
        b = (0,0)
        c = (1,-5)
        vector = getNormalVector(a, b, c)
        self.assertAlmostEqual(vector[0], -3)
        self.assertAlmostEqual(vector[1], 2)
    def testGetMidPoint(self):
        self.assertEqual(getMidPoint((15.0, 15.0), (0,0)), (7.5, 7.5))
        self.assertEqual(getMidPoint((-15.0, -15.0), (0,0)), (-7.5, -7.5))
        self.assertEqual(getMidPoint((-15.0, 15.0), (5,5)), (-5.0, 10.0))
        self.assertEqual(getMidPoint((15.0, -15.0), (5,5)), (10.0, -5.0))
    def testScalarMultiply(self):
        self.assertAlmostEqual( scalarMultiply(3, (15.5, -10)), (46.5,-30))
        self.assertAlmostEqual( scalarMultiply(0, (15.5, -10)), (0,0))
        self.assertAlmostEqual( scalarMultiply(-3.0, (15.5, -10)), (-46.5,30))


if __name__ == "__main__":
    print ('Unit Testing')
    unittest.main()
    