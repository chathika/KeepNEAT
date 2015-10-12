"""
This module contains static functions for determining the state variables. All but
one function in this module are private
"""

import agent
import kUtil, unittest
import math



def __distCenter(inputAgent, center):
    """
    calculate the distance from the given agent to the center of the field
    
    :param inputAgent: the agent you're trying to find the distance from
    :param center: a coordinate representing the center of the field
    
    :type inputAgent: agent
    :type center: tuple of floats
    
    :returns: the distance from the agent's center to the center of the field
    :rtype: float
    """
    return kUtil.getDist(inputAgent.get_noisy_pos(), center)

# get distance between two agents.
def __distAgent(agent1, agent2):
    #return kUtil.getDist(agent1.get_noisy_pos(), agent2.true_pos)
    return kUtil.getDist(agent1.get_noisy_pos(), agent2.get_noisy_pos())

# get angle between three agents.
def __getCosAngle(agent1, agent2, agent3):
    return kUtil.cosTheta(agent1.get_noisy_pos(), agent2.get_noisy_pos(), agent3.get_noisy_pos())



def getStateVarsKeepers(keepers,takers,center):
    """
    Given the array of takers, keepers, and the coordinates of the center of the field,
    Calculate and return the 13 noise free state variables. The simulator should be the
    only class calling this method.
    
    :param keepers: list of all keeper agents
    :param takers: list of all taker agents
    :param center: the coordinate of the center of the field.
    
    :type keepers: list where all elements are of type agent class
    :type takers: list where all elements are of tpe agent class
    :type center: list or tuple of floats
    """
    returnList = []
    keeperActual = sorted(keepers)
    takerActual = sorted(takers)
    
    for i in range(len(keeperActual)):
        returnList.append(__distCenter(keeperActual[i], center))
        
    for i in range(len(takerActual)):
        returnList.append(__distCenter(takerActual[i], center))
    
    
    for i in range(1,len(keeperActual)):
        returnList.append(__distAgent(keeperActual[0], keeperActual[i]))
    
    for i in range(len(takerActual)):
        returnList.append(__distAgent(keeperActual[0], takerActual[i]))
    
    
    returnList.append(min(__distAgent(keeperActual[1], takerActual[0]),__distAgent(keeperActual[1], takerActual[1])))
    returnList.append(min(__distAgent(keeperActual[2], takerActual[0]),__distAgent(keeperActual[2], takerActual[1])))
    returnList.append(max(__getCosAngle(keeperActual[1], keeperActual[0], takerActual[0]),__getCosAngle(keeperActual[1], keeperActual[0], takerActual[1])))
    returnList.append(max(__getCosAngle(keeperActual[2], keeperActual[0],takerActual[0]),__getCosAngle(keeperActual[2], keeperActual[0], takerActual[1])))

    return returnList

# Unit test complete.


class testingCode(unittest.TestCase):
    
    unitTestSigma = 0.01
    
    def test_distCenter(self):
        a1 = agent.agent((0,0),self.unitTestSigma,"Keeper",(0,0))
        self.assertAlmostEqual(__distCenter(a1, (0,0)), 0,1)
        self.assertAlmostEqual(__distCenter(a1, (0,10)), 10,1)
        self.assertAlmostEqual(__distCenter(a1, (10,0)), 10,1)
        self.assertAlmostEqual(__distCenter(a1, (1,1)), math.sqrt(2),1)
        self.assertAlmostEqual(__distCenter(a1, (10,10)), math.sqrt(200),1)
        #self.assertEqual(getVector((0.0,0.0), (-1.0,-1.0)), (-1.0, -1.0))
        #self.assertEqual(getVector((0.5,0.5), (1.0,-1.0)), (0.5, -1.5))
        #self.assertEqual(getVector((0.5,0.4), (-1.0,1.0)), (-1.5, 0.6))
        
    def test__distAgent(self):
        a1 = agent.agent((0,0),self.unitTestSigma,"Keeper",(0,0))
        a2 = agent.agent((10,10),self.unitTestSigma,"Taker",(0,0))
        self.assertAlmostEqual(__distAgent(a1, a2), math.sqrt(200),1)
        
    def test_angleAgent(self):
        a1 = agent.agent((0.010631645330612073, 5.000750148780534),self.unitTestSigma,"Keeper",(0,0))
        a2 = agent.agent((-0.008793653992994898, -0.0003569779220770502),self.unitTestSigma,"Taker",(0,0))
        a3 = agent.agent((5.000443882611892, -0.017223221164217175),self.unitTestSigma,"Keeper",(0,0))
        self.assertAlmostEqual(__getCosAngle(a1, a2, a3), 0, 1)
    
    def test_getStateVars(self):
        #self, worldRef, pos, sigma, agentType, trueBallPos, maxPlayerSpeed, maxBallSpeed, inPossession = False
        import keepAway
        keepAwayWorld = keepAway.keepAway()
        ballPos = (0,0)
        center = (0,0)
        simulatedError = 0.01
        a1 = agent.agent(keepAwayWorld, (10,0),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        a2 = agent.agent(keepAwayWorld,(0,0),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        a3 = agent.agent(keepAwayWorld,(0,5),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        keepers = [a1,a2,a3]
        t1 = agent.agent(keepAwayWorld,(5,5),simulatedError,"Taker",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        t2 = agent.agent(keepAwayWorld,(5,0),simulatedError,"Taker",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        takers = [t1,t2]
        testOut = getStateVarsKeepers(keepers, takers, center)
        actualOut = [0,5,10,5,math.sqrt(50),5,10,5,math.sqrt(50),5,5,math.cos(math.pi / 4.0),1]
        for i in range(len(testOut)):
            self.assertAlmostEqual(testOut[i], actualOut[i], 1)
    #new test case. variables are given in order
    def test_getStateVars2(self):
        import keepAway
        keepAwayWorld = keepAway.keepAway()
        simulatedError = 0.01
        simWidth = 550.0
        simHeight = 357.0
        ballPos = (1/3 * simWidth,1/6 * simHeight)
        c = (simWidth /2.0,simHeight/2.0)
        a1 = agent.agent(keepAwayWorld,(1/3 * simWidth,1/6 * simHeight),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        a2 = agent.agent(keepAwayWorld,(2/3 * simWidth,1/7 * simHeight),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        a3 = agent.agent(keepAwayWorld,(2/5 * simWidth,6/7 * simHeight),simulatedError,"Keeper",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        keepers = [a1,a2,a3]
        t1 = agent.agent(keepAwayWorld,(1/2 * simWidth,5/12 * simHeight),simulatedError,"Taker",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        t2 = agent.agent(keepAwayWorld,(2/5 * simWidth,7/12 * simHeight),simulatedError,"Taker",ballPos, keepAwayWorld.maxPlayerSpeed, keepAwayWorld.maxBallSpeed)
        takers = [t1,t2]
        testOut = getStateVarsKeepers(keepers, takers, c)
        actualOut = [kUtil.getDist((550/3, 59.5), c),
                     kUtil.getDist((550/3 * 2, 51), c),
                     kUtil.getDist((220, 306), c),
                     kUtil.getDist((275, 148.75), c),
                     kUtil.getDist((220, 208.25), c),
                     kUtil.getDist((550/3,59.5), (550/3*2, 51)),
                     kUtil.getDist((550/3,59.5), (220,306)),
                     kUtil.getDist((550/3,59.5), (275, 148.75)),
                     kUtil.getDist((550/3,59.5), (220, 208.25)),
                     min( kUtil.getDist((550/3*2,51), (220, 208.25)), kUtil.getDist((550/3*2,51), (275, 148.75)) ),
                     min( kUtil.getDist((220,306), (220, 208.25)), kUtil.getDist((220,306), (275, 148.75)) ),
                     max(kUtil.cosTheta((550/3*2, 51), (550/3,59.5), (275,148.75)), 
                         kUtil.cosTheta((550/3*2, 51), (550/3,59.5), (220,208.25))),
                     max(kUtil.cosTheta((220,306), (550/3,59.5), (275,148.75)), 
                         kUtil.cosTheta((220,306), (550/3,59.5), (220,208.25))),
                     ]
        for i in range(len(testOut)):
            self.assertAlmostEqual(testOut[i], actualOut[i], 1,"Failed on index: %d" % i)
     
        
        
if __name__ == "__main__":
    print ('Unit Testing')
    unittest.main()
    
