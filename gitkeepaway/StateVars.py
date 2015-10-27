import kUtil
import ball
import agent
import unittest
import math

# get distance of agent from center.
def distCenter(inputAgent, center):
    return kUtil.getDist(inputAgent.noisy_pos, center)

# get distance between two agents.
def distAgent(agent1, agent2):
    return kUtil.getDist(agent1.noisy_pos, agent2.true_pos)

# get angle between three agents.
def getCosAngle(agent1, agent2, agent3):
    return kUtil.cosTheta(agent1.noisy_pos, agent2.noisy_pos, agent3.noisy_pos)

# unit test complete.
class testingCode(unittest.TestCase):
    unitTestSigma = 0.01
    
    def test_distCenter(self):
        a1 = agent.agent((0,0),self.unitTestSigma,"Keeper",(0,0))
        self.assertAlmostEqual(distCenter(a1, (0,0)), 0,1)
        self.assertAlmostEqual(distCenter(a1, (0,10)), 10,1)
        self.assertAlmostEqual(distCenter(a1, (10,0)), 10,1)
        self.assertAlmostEqual(distCenter(a1, (1,1)), math.sqrt(2),1)
        self.assertAlmostEqual(distCenter(a1, (10,10)), math.sqrt(200),1)
        #self.assertEqual(getVector((0.0,0.0), (-1.0,-1.0)), (-1.0, -1.0))
        #self.assertEqual(getVector((0.5,0.5), (1.0,-1.0)), (0.5, -1.5))
        #self.assertEqual(getVector((0.5,0.4), (-1.0,1.0)), (-1.5, 0.6))
        
    def test_distAgent(self):
        a1 = agent.agent((0,0),self.unitTestSigma,"Keeper",(0,0))
        a2 = agent.agent((10,10),self.unitTestSigma,"Taker",(0,0))
        self.assertAlmostEqual(distAgent(a1, a2), math.sqrt(200),1)
        
    def test_angleAgent(self):
        a1 = agent.agent((0.010631645330612073, 5.000750148780534),self.unitTestSigma,"Keeper",(0,0))
        a2 = agent.agent((-0.008793653992994898, -0.0003569779220770502),self.unitTestSigma,"Taker",(0,0))
        a3 = agent.agent((5.000443882611892, -0.017223221164217175),self.unitTestSigma,"Keeper",(0,0))
        self.assertAlmostEqual(getCosAngle(a1, a2, a3), 0, 1)
        
if __name__ == "__main__":
    print ('Unit Testing')
    unittest.main()
    