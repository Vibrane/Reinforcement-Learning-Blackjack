import pygame
import sys
import random
import copy
from pygame.locals import *
from cards import *
from heapq import *
from random import choice


def genCard(cList, xList):
    # Generate and remove a card from cList and append it to xList.
    # Return the card, and whether the card is an Ace
    cA = 0  # boolean for whether it is an ace card
    card = random.choice(cList)
    cList.remove(card)  # card gets removed from this list
    xList.append(card)  # card gets added to this late`
    if card in cardA:  # checks if this card is in the cardA list from cards.py
        cA = 1  # sets the value of cardA to be 1
    return card, cA  # return tuple (card, cA)


def initGame(cList, uList, dList):  # cList is the main list
    # Generates two cards for dealer and user, one at a time for each.
    # Returns if card is Ace and the total amount of the cards per person.
    userA = 0  # keeps track if user has ace
    dealA = 0  # keeps track if dealer has ace
    # calls function to generate card for user
    card1, cA = genCard(cList, uList)
    userA += cA  # add ace count to userA
    card2, cA = genCard(cList, dList)  # generate card for dealer
    dealA += cA  # add ace count to dealer
    # WHY IS THIS HAPPENING ..................................... iDK ... FIND
    # OUT
    dealAFirst = copy.deepcopy(dealA)
    card3, cA = genCard(cList, uList)  # generating card for user
    userA += cA
    card4, cA = genCard(cList, dList)  # generating card for dealer1
    dealA += cA
    # The values are explained below when calling the function
    return getAmt(card1) + getAmt(card3), userA, getAmt(card2) + getAmt(card4), dealA, getAmt(card2), dealAFirst


def make_state(userSum, userA, dealFirst, dealAFirst):  # nothing but a fancy tuple
    # Eliminate duplicated bust cases
    if userSum > 21:
        userSum = 22
    # userSum: sum of user's cards
    # userA: number of user's Aces
    # dealFirst: value of dealer's first card
    # dealAFirst: whether dealer's first card is Ace
    return (userSum, userA, dealFirst, dealAFirst)


def main():
    ccards = copy.copy(cards)
    stand = False
    userCard = []
    dealCard = []
    winNum = 0
    loseNum = 0
    # Initialize Game
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Blackjack')
    font = pygame.font.SysFont("", 20)
    hitTxt = font.render('Hit', 1, black)
    standTxt = font.render('Stand', 1, black)
    restartTxt = font.render('Restart', 1, black)
    MCTxt = font.render('MC', 1, blue)
    TDTxt = font.render('TD', 1, blue)
    QLTxt = font.render('QL', 1, blue)
    gameoverTxt = font.render('End of Round', 1, white)
    # Prepare table of utilities
    MCvalues = {}
    TDvalues = {}
    Qvalues = {}
    Occurence = {}
    # i iterates through the sum of user's cards. It is set to 22 if the user went bust.
    # j iterates through the value of the dealer's first card. Ace is eleven.
    # a1 is the number of Aces that the user has.
    # a2 denotes whether the dealer's first card is Ace.
    for i in range(2, 23):
        for j in range(2, 12):
            for a1 in range(0, 5):
                for a2 in range(0, 2):
                    # -> (userSum, userAceCount, dealerCard, dealerAce)
                    s = (i, a1, j, a2)
                    # utility computed by MC-learning -> initializing to 0
                    MCvalues[s] = 0  # this stores the utility for each state
                    # utility computed by TD-learning -> need to update
                    TDvalues[s] = 0
                    # first element is Q value of "Hit", second element is Q
                    # value of "Stand"
                    Qvalues[s] = [0, 0]
                    # stores number of times encountered each state
                    Occurence[s] = 0

    # userSum: sum of user's cards
    # userA: number of user's Aces
    # dealSum: sum of dealer's cards (including hidden one)
    # dealA: number of all dealer's Aces,
    # dealFirst: value of dealer's first card
    # dealAFirst: whether dealer's first card is Ace
    userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(
        ccards, userCard, dealCard)
    state = make_state(userSum, userA, dealFirst, dealAFirst)
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((80, 150, 15))
    hitB = pygame.draw.rect(background, gray, (10, 445, 75, 25))
    standB = pygame.draw.rect(background, gray, (95, 445, 75, 25))
    MCB = pygame.draw.rect(background, white, (180, 445, 75, 25))
    TDB = pygame.draw.rect(background, white, (265, 445, 75, 25))
    QLB = pygame.draw.rect(background, white, (350, 445, 75, 25))
    autoMC = False
    autoTD = False
    autoQL = False
    # Event loop
    while True:
        # Our state information does not take into account of number of cards
        # So it's ok to ignore the rule of winning if getting 5 cards without
        # going bust
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        if autoMC:
            # Compute the utilities of all states under the policy "Always hit
            # if below 17"
            gamma = 0.9
            G = []  # list of expected goal values -> stores per round value
            # state is already given to us
            run = 0  # amount of times to run the policy
            while (run < 25000):  # computational limit
                run += + 1
                s = copy.deepcopy(state)  # initial state
                simulatedCList = copy.copy(ccards)
                simulatedUserCard = copy.copy(userCard)
                simulatedDealerCard = copy.copy(dealCard)
                episode = []  # simply a sequence of states obtained from s0 to termination
                sUserSum = userSum
                sUserAces = userA
                sDealerSum = dealSum
                sDealFirst = dealFirst
                sDealAce = dealA

                if sUserSum == 21:
                    episode.append((1))  # won if blackjack
                else:  # hit or stand check
                    while sUserSum < 17:  # hit or stand check for user
                        card, cA = genCard(simulatedCList, simulatedUserCard)
                        sUserAces += cA
                        sUserSum += getAmt(card)
                        while sUserSum > 21 and sUserAces > 0:
                            sUserAces -= 1
                            sUserSum -= 10
                        # appended to the episode -> each of these are hit
                        # states
                        episode.append(0)

                    if (sUserSum > 21):  # if bust lose
                        episode.append(-1)
                    elif sUserSum == 21:
                        episode.append(1)
                    else:  # simulate dealer's turn
                        while sDealerSum <= sUserSum and sDealerSum < 17:  # hit or stand check for user
                            card, cA = genCard(
                                simulatedCList, simulatedDealerCard)
                            sDealAce += cA
                            sDealerSum += getAmt(card)
                            while sDealerSum > 21 and sDealAce > 0:
                                sDealAce -= 1
                                sDealerSum -= 10  # -> done simulating the dealer
                        if (sDealerSum > 21):  # if dealer bust, you win
                            episode.append(1)
                        elif sUserSum > sDealerSum:  # win if user > dealer
                            episode.append(1)
                        elif sUserSum < sDealerSum:
                            episode.append(-1)  # loss otherwise
                        elif sUserSum == sDealerSum:  # draw scenario
                            episode.append((0))
                # works because all other hitting is 0 so no need to multiply
                # by gamma
                reward = (gamma ** (len(episode) - 1)) * episode[-1]
                G.append(reward)

            MCvalues[state] = (sum(G) / len(G))

        if autoTD:
            # Compute the utilities of all states under the policy "Always hit if below 17"
            # TDvalues[state] += 1
            # MCvalues[state] += 1
            # MC Learning (erase the dummy +1 of course)
            # Compute the utilities of all states under the policy "Always hit
            # if below 17"
            gamma = 0.9
            tdDict = {}  # this will hold tuple for (U(s), N(s))
            tdDict[state] = [0, 0]

            # state is already given to us
            run = 0  # amount of times to run the policy

            #  make_state(userSum, userA, dealFirst, dealAFirst)
            while (run < 25000):
                run = run + 1
                initial = copy.deepcopy(state)  # initial state
                simulatedCList = copy.copy(ccards)
                simulatedUserCard = copy.copy(userCard)
                simulatedDealerCard = copy.copy(dealCard)
                sUserSum = userSum
                sUserAces = userA
                sDealerSum = dealSum
                sDealAce = dealA
                sDealFirst = dealFirst
                # initial state gets visited once each time for sure per round
                tdDict[initial][1] += 1

                if sUserSum == 21:
                    tdDict[initial] = [1, 1]  # won if blackjack ([1,1])
                else:  # hit or stand check
                    episode = []
                    episode.append((initial, 0))
                    while sUserSum < 17:  # hit or stand check for user
                        card, cA = genCard(simulatedCList, simulatedUserCard)
                        sUserAces += cA
                        sUserSum += getAmt(card)
                        while sUserSum > 21 and sUserAces > 0:
                            sUserAces -= 1
                            sUserSum -= 10
                        tempState = make_state(
                            sUserSum, sUserAces, dealFirst, dealAFirst)
                        episode.append((tempState, 0))  # tuple state, reward
                        if tempState not in tdDict:
                            # appended to the episode -> keep doing stuff while
                            # hitting
                            tdDict[tempState] = [0, 1]
                        else:
                            # just increment the occurence by 1
                            tdDict[tempState][1] += 1
                    if (sUserSum > 21):  # if bust lose
                        episode.append((None, -1))
                    elif sUserSum == 21:
                        episode.append((None, 1))
                    else:
                        # now it is dealer's turn
                        while sDealerSum <= sUserSum and sDealerSum < 17:  # hit or stand check for user
                            card, cA = genCard(
                                simulatedCList, simulatedDealerCard)
                            sDealAce += cA
                            sDealerSum += getAmt(card)
                            while sDealerSum > 21 and sDealAce > 0:
                                sDealAce -= 1
                                sDealerSum -= 10
                        if sDealerSum == 21:  # dealer won
                            episode.append((None, -1))
                        elif sDealerSum > 21:  # if dealer bust, you win
                            episode.append((None, 1))
                        elif sUserSum > sDealerSum:  # win if user > dealer
                            episode.append((None, 1))
                        elif sDealerSum > sUserSum:
                            episode.append((None, -1))
                        elif sUserSum == sDealerSum:
                            episode.append((None, 0))

                    while (len(episode) > 1):
                        after = episode[-1]
                        previous = episode[-2]
                        UofS = tdDict[previous[0]][0]
                        RofS = previous[1]
                        UofNextS = tdDict[after[0]][0] if after[
                            0] is not None else after[1]
                        # this should get the occurences of the state
                        alpha = 11 / (9.0 + tdDict[previous[0]][1])

                        tdDict[previous[0]][0] = UofS + alpha * \
                            (RofS + gamma * (UofNextS) - UofS)
                        episode.pop()
                # for k, v in episode.items():
                #     print(str(k) + "," + str(v))
                # print("user sum was " + str(sUserSum))
                # print("computer sum was: " + str(sDealerSum))
                # print(str(state) + ', ' + str(TDvalues[state][0]))
                # print("-------------------------------------------------------------------------------------------------")

            TDvalues[state] = tdDict[state][0]

        if autoQL:
            # Q-Learning (erase the dummy +1 of course)
            # For each state, compute the Q value of the action "Hit" and
            # "Stand"
            counter = 0
            while counter < 25000:
                counter += 1
                initial = copy.deepcopy(state)  # initial state
                simulatedCList = copy.copy(ccards)
                simulatedUserCard = copy.copy(userCard)
                simulatedDealerCard = copy.copy(dealCard)
                sUserSum = userSum
                sUserAces = userA
                sDealerSum = dealSum
                sDealAce = dealA
                sDealFirst = dealFirst

                current = initial  # the current state we are calculating the stuff for

                keepGoing = True
                while current in Qvalues and keepGoing:
                    Occurence[state] += 1  # update the count of the state
                    # a = pickaction(s, eps, Q)
                    action = None
                    if Qvalues[current][0] > Qvalues[current][1]:
                        action = 'hit'
                    elif Qvalues[current][0] < Qvalues[current][1]:
                        action = 'stand'
                    elif Qvalues[current][0] == Qvalues[current][1]:
                        action = choice(['hit', 'stand'])

                    nextState = None

                    if action == 'hit':
                        card, cA = genCard(simulatedCList, simulatedUserCard)
                        sUserAces += cA
                        sUserSum += getAmt(card)
                        while sUserSum > 21 and sUserAces > 0:
                            sUserAces -= 1
                            sUserSum -= 10
                        nextState = make_state(
                            sUserSum, sUserAces, dealFirst, dealAFirst)

                        QofS = Qvalues[current][0]
                        alpha = 10 / (9.0 * Occurence[current])
                        RofS = None
                        if sUserSum > 21:
                            keepGoing = False  # terminal condition checking
                            RofS = -1
                        elif sUserSum == 21:
                            keepGoing = False  # terminal condition checking
                            RofS = 1
                        else:
                            RofS = 0

                        gamma = 0.9
                        # -> max(a, Q(next_s, a)) does not make sense
                        QofNextS = max(Qvalues[nextState])
                        QofS = QofS + alpha * (RofS + gamma * QofNextS - QofS)

                        Qvalues[current][0] = QofS

                    elif action == 'stand':
                        while sDealerSum <= sUserSum and sDealerSum < 17:  # hit or stand check for user
                            card, cA = genCard(
                                simulatedCList, simulatedDealerCard)
                            sDealAce += cA
                            sDealerSum += getAmt(card)
                            while sDealerSum > 21 and sDealAce > 0:
                                sDealAce -= 1
                                sDealerSum -= 10
                        nextState = make_state(
                            sUserSum, sUserAces, dealFirst, dealAFirst)

                        QofS = Qvalues[current][1]
                        alpha = 10 / (9.0 * Occurence[current])
                        RofS = None
                        if sDealerSum > 21:
                            keepGoing = False  # terminal condition checking
                            RofS = 1
                        elif sDealerSum == 21:
                            keepGoing = False  # terminal condition checking
                            RofS = -1
                        elif sDealerSum > sUserSum:
                            RofS = -1
                            keepGoing = False
                        elif sDealerSum < sUserSum:
                            RofS = 1
                            keepGoing = False
                        elif sDealerSum == sUserSum:
                            keepGoing = False
                            RofS = 0

                        gamma = 0.9
                        # -> max(a, Q(next_s, a)) does not make sense
                        QofNextS = max(Qvalues[nextState])
                        QofS = QofS + alpha * (RofS + gamma * QofNextS - QofS)

                        Qvalues[current][1] = QofS

                    Occurence[nextState] += 1
                    current = nextState

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Clicking the white buttons can start or pause the learning
            # processes
            elif event.type == pygame.MOUSEBUTTONDOWN and MCB.collidepoint(pygame.mouse.get_pos()):
                autoMC = not autoMC
            elif event.type == pygame.MOUSEBUTTONDOWN and TDB.collidepoint(pygame.mouse.get_pos()):
                autoTD = not autoTD
            elif event.type == pygame.MOUSEBUTTONDOWN and QLB.collidepoint(pygame.mouse.get_pos()):
                autoQL = not autoQL
            elif event.type == pygame.MOUSEBUTTONDOWN and (gameover or stand):
                # restarts the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(
                    ccards, userCard, dealCard)
            elif event.type == pygame.MOUSEBUTTONDOWN and not (gameover or stand) and hitB.collidepoint(
                    pygame.mouse.get_pos()):
                # Give player a card
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameover and standB.collidepoint(pygame.mouse.get_pos()):
                # Dealer plays, user stands
                stand = True
                if dealSum == 21:
                    pass
                else:
                    while dealSum <= userSum and dealSum < 17:
                        card, cA = genCard(ccards, dealCard)
                        dealA += cA
                        dealSum += getAmt(card)
                        while dealSum > 21 and dealA > 0:
                            dealA -= 1
                            dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        MCU = font.render('MC-Utility of Current State: %10.2f' %
                          MCvalues[state], 1, black)
        TDU = font.render('TD-Utility of Current State: %10.2f' %
                          TDvalues[state], 1, black)
        QV = font.render('Q values: (Hit) %10.2f (Stand)    %10.2f' %
                         tuple(Qvalues[state]), 1, black)
        winTxt = font.render('Wins: %i' % winNum, 1, white)
        loseTxt = font.render('Losses: %i' % loseNum, 1, white)
        screen.blit(background, (0, 0))
        screen.blit(hitTxt, (39, 448))
        screen.blit(standTxt, (116, 448))
        screen.blit(MCTxt, (193, 448))
        screen.blit(TDTxt, (280, 448))
        screen.blit(QLTxt, (357, 448))
        screen.blit(winTxt, (550, 423))
        screen.blit(loseTxt, (550, 448))
        screen.blit(MCU, (20, 200))
        screen.blit(TDU, (20, 220))
        screen.blit(QV, (20, 240))
        for card in dealCard:
            x = 10 + dealCard.index(card) * 110
            screen.blit(card, (x, 10))
        screen.blit(cBack, (120, 10))
        for card in userCard:
            x = 10 + userCard.index(card) * 110
            screen.blit(card, (x, 295))
        if gameover or stand:
            screen.blit(gameoverTxt, (270, 200))
            screen.blit(dealCard[1], (120, 10))
        pygame.display.update()


if __name__ == '__main__':
    main()
