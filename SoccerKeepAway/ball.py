"""
This is the module that contains the ball class.
"""
import kUtil
import math
import unittest
#note, this class will not contain any noisy values
#all noisy values will be in the agent class ONLY
#all values here will be the TRUE values
class ball():
    """
    The Ball Class
    
    The functionality of the ball class is to keep track of ball's current position,
    current direction it's moving,
    whether or not a player is in possession of it,
    and it stores a maximum speed that it can be passed at. 
    
    :param trueBallPos: a tuple of 2 floats representing the true position of the ball on the field
    :param maxBallSpeed: a floating point value indicating the maximum speed a ball can be passed. by default, agents will pass the ball as fast as possible
    :param inPosession: indicates if a keeper or taker currently has possession of ball.
        
    :type trueBallPos: float,float
    :type maxBallSpeed: float
    :type inPosession: boolean
    """
    #update the ball position, and set the initial direction to None
    def __init__(self, trueBallPos, maxBallSpeed, inPosession = False):
        self.trueBallPos = trueBallPos
        self.trueBallDirection = (0.0,0.0)
        self.inPosession = inPosession
        self.maxBallSpeed = maxBallSpeed
        

    
    def updateCoordinate(self, newCoord):
        """
        update ball coordinate
        
        This function will update the true ball's true position on the field. 
        
        :param newCoord: a tuple representing the true ball coordinates
        
        :type newCoord: float, float

        """
        self.trueBallPos = newCoord
    #UNIT TESTED
    #update the direction vector

    def updateDirection(self, newDirectionVector):
        """
        update the direction component of ball velocity
        
        This function is called upon by the agent class to attempt an
        update to update the direction that the ball is going. The direction
        is stored as a unit vector. 
        
        :param newDirectionVector: a tuple representing the direction 
            that the agent is trying to change the ball to. this vector 
            does not need to be in the form of a unit vector. The direction
            will only be set if the ball is NOT in posession. If the ball is
            in possession, the the direction will remain (0.0,0.0). 
        
        :type newDirectionVector: float, float
        
        :returns: no return
        """
        if not self.inPosession:
            #if no one's posessing it, then it's moving somewhere
            self.trueBallDirection = kUtil.unitVector(newDirectionVector)
        else:
            #ball ain't goin nowhere if someone's posessing it
            self.trueBallDirection = (0.0,0.0)
       
        
    #update whether or not the ball has changed posession
    #if setting the ball posession to false, you HAVE to also give it a direction
    def updatePosession(self, possession):
        """
        update whether or not someone has posession of the ball
        
        :param posession: if true, then the ball is in possession. If false,
            then the ball is NOT in possession. If ball is in posession, also set 
            the ball direction value to (0.0, 0.0)
        
        :type possession: boolean
        
        :returns: no return
        """
        self.inPosession = possession
        if possession == True:
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
    print('Unit Testing') 
    unittest.main()