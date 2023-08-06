import random
from datetime import datetime, timedelta
import unittest
import string

import pandas as pd

from canomaly.searchtools import cumrexpy, _frozenset_target_by_group

# Utilities

def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Tests

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
        expected = pd.Series({'a': ['^[a-z]{5,6}$'], 'b': ['^[a-z]+$']})

        # test function output
        result = cumrexpy(df, 'target', 'group')

        self.assertTrue(result.equals(expected))

    def test_cumrexpy_dates(self):
        # create a sample dataframe with dates
        data = {
            'date': [
                '2018-11-20',
                '2018-11-21',
                '2018-11-22',
                '2018-11-22',
                '2018-11-23',
                '2018-11-24'],
                'email': [
                    'john.doe@example.com',
                    'jane.smith@example.com',
                    'bob-johnson_123@example.com',
                    'sarah@mydomain.co.uk',
                    'frank@mydomain.com',
                    'jessica_lee@mydomain.com'
                    ]
            }
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])

        # expected outcomes
        expected = {
            'email_grouped': {
                '2018-11-20': [
                    '^john\\.doe@example\\.com$'
                    ],
                '2018-11-21': [
                    '^[a-z]{4}\\.[a-z]{3,5}@example\\.com$'
                    ],
                '2018-11-22': [
                    '^[a-z]{4,5}[.@][a-z]+[.@][a-z]+\\.[a-z]{2,3}$',
                    '^bob\\-johnson_123@example\\.com$'
                    ],
                '2018-11-23': [
                    '^frank@mydomain\\.com$',
                    '^[a-z]{4,5}[.@][a-z]+[.@][a-z]+\\.[a-z]{2,3}$',
                    '^bob\\-johnson_123@example\\.com$'
                    ],
                '2018-11-24': [
                    '^frank@mydomain\\.com$',
                    '^[a-z]+[.@_][a-z]+[.@][a-z]+\\.[a-z]{2,3}$',
                    '^bob\\-johnson_123@example\\.com$'
                    ]
                }
            }
        expected = pd.DataFrame(expected)
        expected.index = pd.to_datetime(expected.index)
        expected.index.names = ['date']

        # test function output
        result = cumrexpy(df, 'email', 'date')

        self.assertTrue((expected['email_grouped'] == result).all())
        
        


