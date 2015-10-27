import kUtil
import math
import unittest
#note, this class will not contain any noisy values
#all noisy values will be in the agent class ONLY
#all values here will be the TRUE values
class ball():
    #update the ball position, and set the initial direction to None
    def __init__(self, trueBallPos, maxBallSpeed, inPosession = False):
        self.trueBallPos = trueBallPos
        self.trueBallDirection = (0.0,0.0)
        self.inPosession = inPosession
        self.maxBallSpeed = maxBallSpeed
    
    def updateCoordinate(self, newCoord):
        self.trueBallPos = newCoord
    #UNIT TESTED
    #update the direction vector
    def update(self, newDirectionVector):
        if not self.inPosession:
            #if no one's posessing it, then it's moving somewhere
            self.trueBallDirection = kUtil.unitVector(newDirectionVector)
        else:
            #ball ain't goin nowhere if someone's posessing it
            self.trueBallDirection = (0.0,0.0)
        
    #update whether or not the ball has changed posession
    #if setting the ball posession to false, you HAVE to also give it a direction
    def updatePosession(self, posession):
        self.inPosession = posession
        if posession == True:
            self.trueBallDirection = (0.0,0.0)


class testingCode(unittest.TestCase):
    def test_movingBall(self):
        b = ball((0.0, 1.0), False)
        self.assertEqual(b.trueBallPos, (0.0, 1.0))
        b.update(  (0.0, -5.0)  )
        self.assertEqual(b.trueBallPos, (0.0, -5.0))
        self.assertEqual(b.trueBallDirection, (0.0, -1.0))
        b.update((5.0, 0.0))
        self.assertAlmostEqual(b.trueBallPos, (5.0, 0.0))
        temp = math.sqrt(2.0)/2.0
        self.assertAlmostEqual(b.trueBallDirection[0], temp)
        self.assertAlmostEqual(b.trueBallDirection[1], temp)
        
    def test_posessedBall(self):
        b = ball((0.0, 1.0), False)
        self.assertEqual(b.trueBallPos, (0.0, 1.0))
        b.update(  (0.0, -5.0)  )
        self.assertEqual(b.trueBallPos, (0.0, -5.0))
        self.assertEqual(b.trueBallDirection, (0.0, -1.0))
        b.updatePosession(True)
        b.update((5.0, 0.0))
        self.assertAlmostEqual(b.trueBallPos, (5.0, 0.0))
        self.assertEqual(b.trueBallDirection, None)
        
        
if __name__ == "__main__":
    print ('Unit Testing')
    unittest.main()