Implemented policy evaluation and Q-Learning for Blackjack. The base game engine is from [here](https://github.com/ServePeak/Blackjack-Python/blob/master/blackjack.py). 


The Game
-----
The game more or less follows the standard Blackjack rules. Read the game engine code to see minor simplification 


 Implemented the following algorithms. In all of them, use 0.9 for the discount factor gamma. When the player wins, give reward +1, and when loses, give -1. Currently there is a "draw" case, which you can either give 0 or count it as the player losing in that case. 

Monte Carlo Policy Evaluation

Evaluate the policy "Hit (ask for a new card) if sum of cards is below 17, and Stand (switch to dealer) otherwise" using the Monte Carlo method -- namely, learn the utilities for each state under the policy. One should be able to click the "MC" white button to start or pause the learning process. When the user manually plays the game, the learned utility will be shown for the current state. 

Temporal-Difference Policy Evaluation

Evaluate the policy "Hit (ask for a new card) if sum of cards is below 17, and Stand (switch to dealer) otherwise" using the Temporal-Difference method. One should be able to click the "TD" white button to start or pause the learning process. When the user manually plays the game, the learned utility will be shown for the current state. 

Q-Learning

Implement the Q-learning algorithm. After learning, when the user plays manually, the Q values will be displayed for each action (two choices) to guide the user. 

