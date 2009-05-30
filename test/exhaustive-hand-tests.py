#!/usr/bin/python
# coding=utf8
#!/usr/bin/env python

#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA


import curses
import sys
import random
import time


import settestpath

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
        sys.stdout.write("  %s%s%s\t" % (color_red,
                                         "☠☠FAIL☠☠",
                                         color_normal))
        if not match:
            failed_last_time_counter = 50
        else:
            failed_last_time_counter -= 1
    else:
        sys.stdout.write("          \t")
    msg = "%d tests, %d passed, %d failed (%3.2f%% good)" % (total, good,
            total - good, float(good)/total * 100)
    sys.stdout.write("%s%s%s" % (color_green, msg, color_normal))
    sys.stdout.flush()


def timed_progress(start_time, total):
    current_time = time.time()

    msg = "%s total tests, %0.2f ms/test (avg)" % (total,
            (current_time - start_time)/total * 1000)
    sys.stdout.write("\r")
    sys.stdout.write("%s%s%s" % (color_green, msg, color_normal))
    sys.stdout.flush()


def test_one(test_type, num_players):
    deck = make_deck()

    if test_type == 'rounder':
        from rounder.evaluator import PokerEval
    else:
        from pokereval import PokerEval

    evaluator= PokerEval()
    total = 0
    start_time = time.time()
    while True:
        board, pockets = get_random_setup(list(deck), num_players)

        winners = evaluator.winners(game="holdem",
                pockets=pockets, board=board)['hi']

        total += 1
        timed_progress(start_time, total)


def main(num_players):
    deck = make_deck()

    import pokereval
    from rounder import evaluator

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
    test_type = sys.argv[1]
    if test_type == 'rounder':
        pass
    elif test_type == 'pokereval':
        pass
    elif test_type == 'both':
        pass
    else:
        print "You must specify a test type"
        sys.exit(1)

    if len(sys.argv) >= 3:
        num_players = int(sys.argv[2])
    if len(sys.argv) == 4:
        error_file_name = sys.argv[3]
    print "testing %s" % test_type
    print "running with %s players" % num_players
    print "writing errors to %s" % error_file_name
    print "press ctrl-c to abort"

    error_file = open(error_file_name, 'w')

    try:
        if test_type == 'both':
            main(num_players)
        else:
            test_one(test_type, num_players)
    except KeyboardInterrupt:
        print ""
