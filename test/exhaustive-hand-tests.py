#!/usr/bin/python
# coding=utf8

import curses
import sys
import random

import pokereval

import settestpath
from rounder import evaluator

curses.setupterm()
color_normal = curses.tigetstr('sgr0')
color_red = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_RED)
color_green = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_GREEN)

error_file = None


def make_deck():
    suits = ('h', 'd', 'c', 's')
    ranks = ('2', '3', '4', '5', '6', '7', '8', '9', 't', 'j', 'q', 'k', 'a')

    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append(rank + suit)

    return deck

def get_random_cards(deck, num_cards):
    cards = []
    while len(cards) < num_cards:
        card = random.choice(deck)
        deck.remove(card)
        cards.append(card)

    return cards

def get_random_setup(deck, num_players):
    board = get_random_cards(deck, 5)
    pockets = []
    while len(pockets) < num_players:
        pockets.append(get_random_cards(deck, 2))

    return board, pockets


def error(msg):
    print >> error_file, msg

failed_last_time_counter = 0

def progress(total, good, match=True):
    global failed_last_time_counter
    sys.stdout.write("\r")
    if not match or failed_last_time_counter > 0:
        sys.stdout.write("  %s%s%s\t" %(color_red, "☠☠FAIL☠☠", color_normal))
        if not match:
            failed_last_time_counter = 50
        else:
            failed_last_time_counter -= 1
    else:
        sys.stdout.write("          \t")
    msg = "%d tests, %d passed (%3.0f%% good)" % (total, good,
            float(good)/total * 100)
    sys.stdout.write("%s%s%s" % (color_green, msg, color_normal))
    sys.stdout.flush()

def main(num_players):
    deck = make_deck()

    pypoker_evaluator = pokereval.PokerEval()
    rounder_evaluator = evaluator.PokerEval()

    total = 0
    good = 0
    while True:
        board, pockets = get_random_setup(list(deck), num_players)

        pypoker_winners = pypoker_evaluator.winners(game="holdem",
                pockets=pockets, board=board)['hi']
        rounder_winners = rounder_evaluator.winners(game="holdem",
                pockets=pockets, board=board)['hi']

        total += 1

        if pypoker_winners != rounder_winners:
            error("== FAIL ==")
            error("%s %s" % (board, pockets))
            error("pypoker: %s" % pypoker_winners)
            error("rounder: %s" % rounder_winners)
            error("")
            progress(total, good, False)
        else:
            good += 1
            progress(total, good, True)


if __name__ == "__main__":
    num_players = 2
    error_file_name = "hand-match-errors.txt"
    if len(sys.argv) >= 2:
        num_players = int(sys.argv[1])
    if len(sys.argv) == 3:
        error_file_name = sys.argv[2]
    print "running with %s players" % num_players
    print "writing errors to %s" % error_file_name
    print "press ctrl-c to abort"

    error_file = open(error_file_name, 'w')

    try:
        main(num_players)
    except KeyboardInterrupt:
        print ""
