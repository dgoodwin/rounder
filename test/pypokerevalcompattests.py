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

"""
Tests originally for exploring usage of the pypoker-eval library,
now kept for testing rounder.evaluator's pypoker-eval compatibility
"""

import unittest
import settestpath

from rounder.evaluator import PokerEval

class PyPokerEvalCompatTests(unittest.TestCase):
    """ Tests for pypoker-eval compatibility. """

    def test_single_winner(self):
        evaluator = PokerEval()
        cards1 = ["ac", "ah"]
        cards2 = ["kc", "kd"]
        cards3 = ["2h", "5d"]
        pockets = [cards1, cards2, cards3]
        board = ["as", "ks", "2d", "2s", "5c"]
        result = evaluator.winners(game="holdem", pockets=pockets, board=board)
        self.assertEquals(1, len(result['hi']))
        self.assertEquals(0, result['hi'][0])

    def test_tie(self):
        evaluator = PokerEval()
        cards1 = ["ac", "ah"]
        cards2 = ["as", "ad"]
        cards3 = ["2h", "5d"]
        pockets = [cards1, cards2, cards3]
        board = ["7s", "ks", "td", "ts", "5c"]
        result = evaluator.winners(game="holdem", pockets=pockets, board=board)
        self.assertEquals(2, len(result['hi']))
        self.assertEquals(0, result['hi'][0])
        self.assertEquals(1, result['hi'][1])

    def test_board_plays(self):
        evaluator = PokerEval()
        cards1 = ["ac", "kh"]
        cards2 = ["as", "qd"]
        cards3 = ["2h", "5d"]
        pockets = [cards1, cards2, cards3]
        board = ["7s", "7d", "7c", "ts", "tc"]
        result = evaluator.winners(game="holdem", pockets=pockets, board=board)
        self.assertEquals(3, len(result['hi']))

    def test_premature_hand_end(self):
        evaluator = PokerEval()
        cards1 = ["ac", "ah"]
        pockets = [cards1]
        board = []
        result = evaluator.winners(game="holdem", pockets=pockets, board=board)
        self.assertEquals(1, len(result['hi']))
        self.assertEquals(0, result['hi'][0])



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PyPokerEvalCompatTests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
