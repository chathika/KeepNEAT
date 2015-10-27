import keepAway


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
    print("execute hand coded")
elif (mode == "manual"):
    print("execute manual debugging mode")
world.gameLoop(mode)
world.pause("game over. Final Score: ", world.keeperScore)
