""" Tests for the rounder.card module. """

import unittest

import settestpath

class FakeTests(unittest.TestCase):
    def test_nothing(self):
        pass



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FakeTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
