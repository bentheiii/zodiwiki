from typing import Dict, List

from collections import defaultdict
from pathlib import Path

from zodilib.page import Page, split_terms


class Wiki:
    @staticmethod
    def linkto(page):
        if isinstance(page, Page):
            return page.linkto
        return '/page/'+page

    def __init__(self):
        self.pages: Dict[str, Page] = {}  # page keys are always in lowercase
        self.tags: Dict[str, List[Page]] = defaultdict(list)  # tag names are always lowercase

    def add_page(self, page: Page):
        for title in page.titles:
            p = self.pages.setdefault(title.lower(), page)
            if p is not page:
                raise Exception('multiple pages sharing a title ' + title)
        for t in page.tags:
            self.tags[t].append(page)

    def match(self, main, hints):
        main_terms = split_terms(main)
        hint_terms = split_terms(hints)
        for p in self.pages.values():
            s = p.score(main_terms, hint_terms)
            yield p, s

    def best_match(self, main, hints):
        best = None, -1
        main_terms = split_terms(main)
        hint_terms = split_terms(hints)
        for p in self.pages.values():
            s = p.score(main_terms, hint_terms, cutoff=best[-1])
            if s > best[-1]:
                best = p, s
        return best[0]

    def __getitem__(self, name):
        name = name.lower()
        return self.pages.get(name), self.tags.get(name)

    def __contains__(self, item):
        return (item in self.pages) or (item in self.tags)

    @classmethod
    def from_dir(cls, dir_path):
        ret = cls()
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise ValueError('path id not a directory')
        for page_path in dir_path.glob('[!_]*.md'):
            with page_path.open() as r:
                page = Page(r.read())
            ret.add_page(page)
        return ret
