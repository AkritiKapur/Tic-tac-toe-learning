import pickle
from interface import Game, QPlayer

epsilon = 0.9
player1 = QPlayer(mark="X", epsilon=epsilon)
player2 = QPlayer(mark="O", epsilon=epsilon)
game = Game(player1, player2, True)

N_episodes = 10
for episodes in range(N_episodes):
    game.start()
    game.reset()

Q = game.Q
print Q

filename = "Q_training_Nepisodes_{}.p".format(N_episodes)
pickle.dump(Q, open(filename, "wb"))
