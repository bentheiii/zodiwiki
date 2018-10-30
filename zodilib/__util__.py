from sortedcontainers import SortedKeyList

from operator import itemgetter


class MaxStore:
    """
    >>> x = MaxStore()
    >>> x.add('a',0)
    True
    >>> list(x)
    [(0, 'a')]
    >>> x.add('b',0)
    True
    >>> list(x)
    [(0, 'a'), (0, 'b')]
    >>> x.add('c', 2)
    True
    >>> list(x)
    [(2, 'c')]
    >>> x.add('d', 0)
    False
    >>> list(x)
    [(2, 'c')]
    >>> x.add('e', 1.9)
    True
    >>> list(x)
    [(1.9, 'e'), (2, 'c')]
    >>> x.add('f', 2.2)
    True
    >>> list(x)
    [(2, 'c'), (2.2, 'f')]
    """

    def __init__(self, margin=0.9):
        self.store = SortedKeyList(key=itemgetter(0))
        self.margin = margin

    @property
    def cutoff(self):
        if not self.store:
            return 0
        return self.store[-1][0] * self.margin

    @property
    def cuton(self):
        if not self.store:
            return 0
        return self.store[-1][0]

    def add(self, key, score):
        if score < self.cutoff:
            return False
        purge = score > self.cuton
        self.store.add((score, key))
        if purge:
            purge_ind = self.store.bisect_key_left(self.cutoff)
            del self.store[:purge_ind]
        return True

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __bool__(self):
        return bool(self.store)

    def best(self):
        return self.store[-1]

    def best_key(self):
        return self.best()[1]

__all__ = ['MaxStore']