from typing import Set, Dict, Iterable, List

import re

import markdown
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.meta import MetaExtension

from zodilib.extensions import HintedWikiLinkExtension, AutoTitleExtension

md = markdown.Markdown(extensions=[
    FootnoteExtension(),
    TocExtension(),
    TableExtension(),
    MetaExtension(),
    AutoTitleExtension(),
    HintedWikiLinkExtension()
])

tag_split_pattern = re.compile('\s*,\s*')

term_split_pattern = re.compile('[^0-9a-zA-Z]')

term_length_multiplier = 1
start_of_term_multiplier = 2
exact_match_multiplier = 3
title_term_multiplier = 2
tag_term_multiplier = 1
main_term_multiplier = 2
hint_term_multiplier = 1

max_score = exact_match_multiplier * title_term_multiplier

term_blacklist = {
    'the', 'in', 'of', 'a', 'on', 'to', 'it', 'as', 'be', 'nt', 's', ''
}


def split_terms(joined: str):
    return [t.lower() for t in term_split_pattern.split(joined) if t.lower() not in term_blacklist]


def merge_keys(d: dict, *keys: str):
    ret = []
    for k in keys:
        ret.extend(d.get(k, ()))
    return ret


# Note, all strings are stored as case-invariant, but are compared by lower-case
class Page:
    @classmethod
    def read(cls, source):
        return cls(source.read())

    def __init__(self, md: str, ):
        self.titles: List[str] = []  # titles here are stored case-insensitive
        self.md = md
        self.html: str = None
        self.tags: Set[str] = set()  # all tags are stored in lowercase
        self.terms: Dict[str, int] = None  # all terms are stored in lowerspace
        self.load()
        self.update_terms()

    @property
    def title(self):
        return self.titles[0]

    @property
    def linkto(self):
        return '/page/'+self.title

    def load(self):
        self.html = md.convert(self.md)
        meta: Dict[str, Iterable[str]] = md.Meta
        md.reset()

        try:
            titles = merge_keys(meta, 'title', 'titles')
        except KeyError:
            raise Exception('page must have a title')  # todo get path? maybe from from_dir
        self.titles.extend(titles)

        m_tags = merge_keys(meta, 'tag', 'tags')
        for tags in m_tags:
            self.tags.update(x.lower() for x in tag_split_pattern.split(tags) if x)

    def update_terms(self):
        self.terms = {}
        for title in self.titles:
            for t in split_terms(title):
                self.add_term(t, title_term_multiplier)
        for tag in self.tags:
            for t in split_terms(tag):
                self.add_term(t, tag_term_multiplier)

    def add_term(self, term, score):
        term = term.lower()
        if self.terms.get(term, -1) < score:
            self.terms[term] = score

    def _score(self, term):
        ret = 0
        for k, v in self.terms.items():
            f = k.find(term)
            if f == -1:
                continue
            score = v
            if len(k) == len(term):
                score *= exact_match_multiplier
            elif f == 0:
                score *= start_of_term_multiplier

            if score > ret:
                ret = score
                if ret == max_score:
                    return ret
        return ret

    def score(self, main_terms, hint_terms, cutoff=0):
        def check_cutoff(to_reduce):
            nonlocal max_points_left
            needed = cutoff - total
            max_points_left -= to_reduce * max_score
            return needed > max_points_left

        total = 0
        max_points_left = (len(main_terms) * main_term_multiplier + len(hint_terms) * hint_term_multiplier) * max_score
        for m in main_terms:
            total += self._score(m) * main_term_multiplier
            if check_cutoff(main_term_multiplier):
                return -1
        for hint in hint_terms:
            total += self._score(hint) * hint_term_multiplier
            if check_cutoff(hint_term_multiplier):
                return -1
        return total

    def __str__(self):
        return '<wiki page titled: ' + str(self.titles) + '>'
