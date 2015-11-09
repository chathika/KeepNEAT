"""
This is the entry point for the simlation. It will initialize everything
and also ask the user which agent they want to run
"""
import keepAway

class runme():
    """
    The runme class
    
    It's functionality is just to initialize everything and start the simulation.
    There are no inputs or outputs for the function itself, other than the default
    self argument. Open up a prompt asking the user what mode they would like to play in,
    and send the response to an instance of the keepAway class. After that class terminates
    either by user interupt, or by the game ending, print out the results. 
    """
    def __init__(self):
        world = keepAway.keepAway(0.000000001, alreadyTrained = False)
        mode =world.game_intro()
        
        if (mode == "hyperNEAT"):
            #hyperNEAT mode
            print("execute hyperNEAT") 
        elif (mode == "NEAT"):
            #NEAT mode
            print("execute NEAT")
        elif (mode == "hand_coded"):
            #hand coded mode
            print("execute hand coded")
        elif (mode == "manual"):
            print("execute manual debugging mode")
        world.gameLoop(mode, turnOnGrid = False)
        world.pause("game over. Final Score: ", world.keeperScore)
        

        
        
if __name__ == "__main__":
    runme()
