from typing import Dict, List

from collections import defaultdict
from pathlib import Path

import markdown
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.meta import MetaExtension

from zodilib.extensions import HintedWikiLinkExtension, AutoTitleExtension, SizeEnabledImageExtension
from zodilib.page import Page, split_terms
from zodilib.exceptions import PageLoadError
from zodilib.__util__ import *


class Wiki:
    DEFAULT_MD_EXTENSIONS = [
        FootnoteExtension(),
        TocExtension(),
        TableExtension(),
        MetaExtension(),
        AutoTitleExtension(),
        HintedWikiLinkExtension(),
        SizeEnabledImageExtension()
    ]

    @staticmethod
    def link_to(page):
        return getattr(page, 'link_to', None) or '/page/' + page

    def __init__(self, md_extensions=[...]):
        if md_extensions[-1] is ...:
            md_extensions = md_extensions[:-1] + self.DEFAULT_MD_EXTENSIONS
        self.md = markdown.Markdown(extensions=md_extensions)

        self.title = 'UNSET TITLE'
        self.logo = '/static/logo.png'
        self.root_dir_path = None
        self.rsc_dir_path = None

        self.titles: Dict[str, Page] = {}  # page keys are always in lowercase
        self.tags: Dict[str, List[Page]] = defaultdict(list)  # tag names are always lowercase
        self.unique_pages: List[Page] = []

    def set_root_path(self, path: Path):
        self.root_dir_path = path
        self.rsc_dir_path = path / 'rsc'

    def scan_path(self, clear=False):
        if clear:
            self.clear_pages()

        conf_path = self.root_dir_path / 'config.py'
        if conf_path.is_file():
            exec(conf_path.read_text(), {'wiki': self})

        for page_path in self.root_dir_path.glob('[!_]*.md'):
            try:
                with page_path.open() as r:
                    page = Page(r.read(), self)
            except PageLoadError as e:
                raise PageLoadError('error loading page ' + str(page_path)) from e
            self.add_page(page)

    def clear_pages(self):
        self.titles.clear()
        self.tags.clear()
        self.unique_pages.clear()

    def add_page(self, page: Page):
        for title in page.titles:
            p = self.titles.setdefault(title.lower(), page)
            if p is not page:
                raise Exception('multiple pages sharing a title ' + title)
        for t in page.tags:
            self.tags[t].append(page)
        self.unique_pages.append(page)

    def match(self, main, hints):
        main_terms = split_terms(main)
        hint_terms = split_terms(hints)
        for p in self.unique_pages:
            s = p.score(main_terms, hint_terms)
            yield p, s

    def best_match(self, main, hints)->MaxStore:
        store = MaxStore()
        main_terms = split_terms(main)
        hint_terms = split_terms(hints)
        for p in self.unique_pages:
            s = p.score(main_terms, hint_terms, cutoff=store.cutoff)
            store.add(p, s)
        return store

    def __getitem__(self, name):
        name = name.lower()
        return self.titles.get(name), self.tags.get(name)

    def __contains__(self, item):
        return (item in self.titles) or (item in self.tags)

    @classmethod
    def from_dir(cls, dir_path):
        ret = cls()
        dir_path = Path(dir_path).absolute()
        if not dir_path.is_dir():
            raise ValueError('path id not a directory')
        ret.set_root_path(dir_path)
        ret.scan_path()
        return ret
