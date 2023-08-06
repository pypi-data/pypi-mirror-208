import unittest
import pandas as pd

from canomaly.searchtools import cumrexpy, _frozenset_target_by_group

class TestFunctions(unittest.TestCase):
    
    def test_frozenset_target_by_group(self):
        # create a sample dataframe
        data = {'target': [1, 2, 3, 4, 5],
                'group': ['a', 'a', 'b', 'b', 'b']}
        df = pd.DataFrame(data)

        # expected output
        expected = pd.DataFrame({'group': ['a', 'b'],
                                 'target_grouped': [frozenset([1, 2]), frozenset([3, 4, 5])]})

        # test function output
        result = _frozenset_target_by_group(df, 'target', 'group')
        self.assertTrue(result.equals(expected))

    def test_cumrexpy(self):
        # create a sample dataframe
        data = {'target': ['apple', 'banana', 'cherry', 'date', 'elderberry'],
                'group': ['a', 'a', 'b', 'b', 'b']}
        df = pd.DataFrame(data)

        # expected output
        expected = pd.Series([{'apple'}, {'apple', 'banana'}, {'cherry'}, {'cherry', 'date'}, {'cherry', 'date', 'elderberry'}])

        # test function output
        result = cumrexpy(df, 'target', 'group')

        self.assertTrue(result.equals(expected))


