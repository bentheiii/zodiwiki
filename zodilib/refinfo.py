from typing import Iterable, Set, Tuple, Dict

from collections import defaultdict

from zodilib.page import Page


class RefInfo:
    def __init__(self, page):
        self.page = page
        self.links_in: Set[Page] = set()
        self.links_out: Set[Page] = set()
        self.bad_links: Dict[str, Set[str]] = defaultdict(set)

    def add_outs(self, outs: Iterable[Page]):
        self.links_out.update(outs)

    def add_in(self, in_: Page):
        self.links_in.add(in_)

    def add_bads(self, bad: Iterable[Tuple[str, str]]):
        for r, b in bad:
            self.bad_links[r].add(b)
