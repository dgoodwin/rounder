import unittest
import settestpath
import configureLogging

# Import all test modules here:
import cardtests
import decktests

from unittest import TestSuite

def suite():
    # Append all test suites here:
    return TestSuite((
        cardtests.suite(),
        decktests.suite(),
    ))

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
