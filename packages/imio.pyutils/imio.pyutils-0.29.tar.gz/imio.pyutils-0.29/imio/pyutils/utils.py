# -*- coding: utf-8 -*-
#
# python utils methods
# IMIO <support@imio.be>
#
from collections import OrderedDict, defaultdict
from itertools import chain
from operator import methodcaller

import copy
import itertools
import logging
import time
import timeit


def all_of_dict_values(dic, keys, labels=[], sep=u'='):
    """Returns a not empty values list from a dict following given keys.

    :param dic: input dictionary
    :param keys: searched keys
    :param labels: corresponding labels
    :param sep: separator between label and value
    :return: list with corresponding values.
    """
    if labels and len(labels) != len(keys):
        raise ValueError(u'labels length must be the same as keys length')
    ret = []
    for i, key in enumerate(keys):
        if dic.get(key):
            ret.append(labels and u'{}{}{}'.format(labels[i], labels[i] and sep or u'', dic[key]) or dic[key])
    return ret


def append(lst, value):
    lst.append(value)
    return value


def ftimed(f, nb=100, fmt='{:.7f}'):
    duration, ret = timed(f, nb=nb)
    return fmt.format(duration), ret


def get_clusters(numbers=[], separator=", "):
    """Return given p_numbers by clusters.
       When p_numbers=[1,2,3,5,6,8,9,10,15,17,20],
       the result is '1-3, 5-6, 8-10, 15, 17, 20'."""
    clusters = itertools.groupby(numbers, lambda n, c=itertools.count(): n - next(c))
    res = []
    for group, cluster in clusters:
        clust = list(cluster)
        if len(clust) > 1:
            res.append('{0}-{1}'.format(clust[0], clust[-1]))
        else:
            res.append('{0}'.format(clust[0]))
    return separator.join(res)


def insert_in_ordereddict(dic, value, after_key='', at_position=None):
    """Insert a tuple in an new Ordereddict.

        :param dic: the original OrderedDict
        :param value: a tuple (key, value) that will be added at correct position
        :param after_key: key name after which the tup is added
        :param at_position: position at which the tup is added. Is also a default if after_key is not found
        :return: a new OrderedDict or None if insertion position is undefined
    """
    position = None
    if after_key:
        position = odict_index(dic, after_key, delta=1)
    if position is None and at_position is not None:
        position = at_position
    if position is None:
        return None
    if position >= len(dic.keys()):
        return OrderedDict(list(dic.items()) + [value])
    tuples = []
    for i, tup in enumerate(dic.items()):
        if i == position:
            tuples.append(value)
        tuples.append(tup)
    if not tuples:  # dic was empty
        tuples.append(value)
    return OrderedDict(tuples)


def iterable_as_list_of_list(lst, cols=1):
    """Transform an iterable as list of list.

    :param lst: input iterable
    :param cols: number of columns in the sublists
    :return: list of lists
    """
    res = []
    sublist = []
    for i, item in enumerate(lst, start=1):
        sublist.append(item)
        if not i % cols:
            if sublist:
                res.append(sublist)
            sublist = []
    # put the last sublist in res
    if sublist:
        res.append(sublist)
    return res


def merge_dicts(dicts, as_dict=True):
    """Merge dicts, extending values of each dicts,
       useful for example when the value is a list.

    :param dicts: the list of dicts to mergeinput iterable
    :param as_dict: return a dict instead the defaultdict instance
    :return: a single dict (or defaultdict)
    """
    dd = defaultdict(list)

    # iterate dictionary items
    dict_items = map(methodcaller('items'), dicts)
    for k, v in chain.from_iterable(dict_items):
        dd[k].extend(v)
    return as_dict and dict(dd) or dd


def odict_index(odic, key, delta=0):
    """Get key position in an ordereddict"""
    for i, k in enumerate(odic):
        if k == key:
            return i + delta
    return None


def odict_pos_key(odic, pos):
    """Get key corresponding at position"""
    keys = [k for k in odic]
    if pos < 0:
        return None
    else:
        return keys[pos]


def one_of_dict_values(dic, keys):
    """Take the first value not empty in a dict following given keys"""
    for key in keys:
        if dic.get(key):
            return dic[key]
    return None


def replace_in_list(lst, value, replacement, generator=False):
    """
        Replace a value in a list of values.
        :param lst: the list containing value to replace
        :param value: the value to be replaced
        :param replacement: the new value to replace with
        :param generator: will return a generator instead a list when set to True
        :return: a new list/generator with replaced values
    """
    def _replacer(lst, value, replacement):
        new_lst = list(lst)
        for item in new_lst:
            if item == value:
                yield replacement
            else:
                yield item
    res = _replacer(lst, value, replacement)
    if not generator:
        res = list(res)
    return res


def safe_encode(value, encoding='utf-8'):
    """Converts a value to encoding, only when it is not already encoded."""
    if isinstance(value, unicode):
        return value.encode(encoding)
    return value


def setup_logger(logger, replace=logging.StreamHandler, level=20):
    """Modify logger handler level

    :param logger: logger to modify
    :param replace: handler type to replace
    :param level: level to set
    """
    for i_c, container in enumerate((logger, logger.parent)):
        found = [i for i, hdl in enumerate(container.handlers) if isinstance(hdl, logging.StreamHandler)]
        if found:
            if i_c:
                logger.parent = container = copy.copy(logger.parent)
            break
    else:
        return
    idx = found[0]
    osh = copy.copy(container.handlers[idx])
    osh.setLevel(level)
    # remove handler from original container handlers (often parent)
    container.handlers = [hdl for i, hdl in enumerate(container.handlers) if i != idx]
    # put handler in logger handlers
    logger.handlers.append(osh)
    logger.setLevel(level)


def sort_by_indexes(lst, indexes, reverse=False):
    """Sort a list following a second list containing the order"""
    return [val for (_, val) in sorted(
        zip(indexes, lst), key=lambda x: x[0], reverse=reverse)]


def timed(f, nb=100):  # TODO must be removed and replaced by timeit
    start = time.time()
    for i in range(nb):
        ret = f()
    return (time.time() - start) / nb, ret  # difference of time is float


def time_elapsed(start, cond=True, msg=u'', dec=3, min=0.0):
    """Print elapsed time from start.

    :param start: start time gotten from time_start function
    :param cond: print condition
    :param msg: message to include in print
    :param dec: decimal precision (default to 3)
    :param min: minimal elapsed value print

    Usage:
    from imio.pyutils.utils import time_elapsed, time_start
    start = time_start()
    ...
    time_elapsed(start, cond=obj.id=='myid', msg=u'myfunc')
    """
    if not cond:
        return
    elapsed = timeit.default_timer() - start
    if elapsed < min:
        return
    print(u"* {{}}: {{:.{}f}} seconds".format(dec).format(msg, elapsed))


def time_start():
    """To be used with time_elapsed."""
    return timeit.default_timer()
