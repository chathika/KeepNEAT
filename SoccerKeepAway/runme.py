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
        world = keepAway.keepAway()
        mode =world.game_intro()
        
        if (mode == "q_learning"):
            #q learning mode
            print("execute q learning") 
        elif (mode == "sarsa"):
            #sarsa mode
            print("execute sarsa")
        elif (mode == "hand_coded"):
            #sarsa mode
            #print("execute hand coded")
            print("execute hand coded")
        elif (mode == "manual"):
            print("execute manual debugging mode")
        world.gameLoop(mode)
        world.pause("game over. Final Score: ", world.keeperScore)
        
        
if __name__ == "__main__":
    runme()
