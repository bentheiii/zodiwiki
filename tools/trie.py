from typing import MutableMapping, Iterable, TypeVar

from itertools import chain

KE = TypeVar('KE')
V = TypeVar('V')

_stop = object()


class Trie(MutableMapping[Iterable[KE], V]):
    """
    >>> t = Trie()
    >>> t['a'] = t['ab'] = t['abracadabra'] = t['kadabra'] = None
    >>> t.longest_prefix('ac')
    'a'
    >>> t.longest_prefix('a')
    'a'
    >>> t.longest_prefix('cold')
    >>> t.longest_prefix('kaddie')
    >>> t.longest_prefix('abra')
    'ab'
    >>> t.longest_prefix('abracadabra')
    'abracadabra'
    """
    def __init__(self):
        self.children = {}
        self._dict = {}

    def __delitem__(self, key):
        raise NotImplemented

    def __setitem__(self, key: Iterable[KE], value: V):
        child = self.children
        for e in key:
            if e in child:
                child = child[e]
            else:
                child[e] = {}
                child = child[e]
        if _stop in child:
            raise NotImplemented('duplicate key ' + str(key))
        child[_stop] = key
        self._dict[key] = value

    def __getitem__(self, item):
        return self._dict[item]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def longest_prefix(self, superword: Iterable[KE]):
        ret = None
        child = self.children
        for c in chain(superword, (None,)):
            if _stop in child:
                ret = child[_stop]
            if c in child:
                child = child[c]
            else:
                break
        return ret
