# -*- coding: utf-8 -*-
#
# tests utis methods
# IMIO <support@imio.be>
#
from imio.pyutils.utils import all_of_dict_values
from imio.pyutils.utils import get_clusters
from imio.pyutils.utils import merge_dicts
from imio.pyutils.utils import one_of_dict_values
from imio.pyutils.utils import replace_in_list
from imio.pyutils.utils import sort_by_indexes

import types
import unittest


class TestUtils(unittest.TestCase):
    """ """

    def test_all_of_dict_values(self):
        self.assertListEqual(all_of_dict_values({1: None, 2: 'Good', 3: '', 4: 'job'}, [1, 2, 3, 4]),
                             ['Good', 'job'])
        self.assertListEqual(all_of_dict_values({1: None, 2: 'Good', 3: '', 4: 'job'}, [2, 4],
                                                labels=[u'Two', u'Four']),
                             ['Two=Good', 'Four=job'])
        self.assertListEqual(all_of_dict_values({1: None, 2: 'Good', 3: '', 4: 'job'}, [2, 4],
                                                labels=[u'Two', u'']),
                             ['Two=Good', 'job'])
        self.assertRaises(ValueError, all_of_dict_values, {}, [1], labels=[1, 2])
        self.assertListEqual(all_of_dict_values({}, [1, 2]), [])

    def test_get_clusters(self):
        self.assertEqual(get_clusters([1, 2, 3, 5, 6, 8, 10, 15]),
                         '1-3, 5-6, 8, 10, 15')
        self.assertEqual(get_clusters([1, 2, 3, 5, 5.1, 5.3, 6, 8, 10, 15]),
                         '1-3, 5, 5.1, 5.3, 6, 8, 10, 15')
        self.assertEqual(get_clusters([1, 2, 4, 5, 15], separator="|"),
                         '1-2|4-5|15')

    def test_merge_dicts(self):
        self.assertEqual(merge_dicts([{'a': [1]}, {'a': [2]}]),
                         {'a': [1, 2]})
        self.assertEqual(
            merge_dicts([{'a': [1], 'b': [0]}, {'a': [2]}]),
            {'a': [1, 2], 'b': [0]})
        self.assertEqual(
            merge_dicts([
                {'a': [1], 'b': [0]},
                {'a': [2]},
                {'a': [2], 'b':[1], 'c': [4]}]),
            {'a': [1, 2, 2], 'b': [0, 1], 'c': [4]})

    def test_one_of_dict_values(self):
        self.assertEqual(one_of_dict_values({1: None, 3: '', 4: 'job'}, [1, 2 , 3, 4]), 'job')

    def test_replace_in_list(self):
        self.assertEqual(replace_in_list([1, 2, 3], 1, 4), [4, 2, 3])
        self.assertEqual(replace_in_list([1, 2, 3], 4, 5), [1, 2, 3])
        self.assertEqual(replace_in_list([1, 2, 3, 1], 1, 5), [5, 2, 3, 5])
        # generator
        res = replace_in_list([1, 2, 3], 1, 4, generator=True)
        self.assertTrue(isinstance(res, types.GeneratorType))
        self.assertEqual(list(res), [4, 2, 3])

    def test_sort_by_indexes(self):
        lst = ["a", "b", "c", "d", "e", "f", "g"]
        indexes = [1, 3, 5, 2, 4, 6, 6]
        self.assertEqual(sort_by_indexes(lst, indexes),
                         ['a', 'd', 'b', 'e', 'c', 'f', 'g'])
        lst = ["a", "b", "c", "d", "e"]
        indexes = [1, 3, 2, 9, 9]
        self.assertEqual(sort_by_indexes(lst, indexes),
                         ['a', 'c', 'b', 'd', 'e'])
