import re

from markdown.inlinepatterns import Pattern
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
from markdown.util import etree


class HintedWikiLinkExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add("hintedwikilink", HintedWikiLinkPattern(), '>html')


class HintedWikiLinkPattern(Pattern):
    Pattern = r'(?<!\\){(?P<main>[^{}|]+)(\|(?P<hints>([^{}|])*))?}'

    def __init__(self, pattern=Pattern):
        super().__init__(pattern)

    def getCompiledRegExp(self):
        return super().getCompiledRegExp()

    def handleMatch(self, m):
        ret = etree.Element('a')
        ret.text = m['main']
        ret.set('href', f'/bestmatch/{m["main"]}/{m["hints"] or ""}')
        return ret


class AutoTitleExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add("autotitle", AutoTitleProcessor(md), ">meta")


class AutoTitleProcessor(Preprocessor):
    def run(self, lines):
        pre_title_len = 0
        for l in lines:
            if l.startswith('# '):
                title = l[len('# '):]
                break
            else:
                pre_title_len += 1
        else:
            return lines
        '''
        if not pre_title_len:
            return ['titles: ' + title, ''] + lines
        return ['titles: ' + title] + lines[:pre_title_len] + lines[pre_title_len:]
        '''
        self.markdown.Meta.setdefault('titles', []).append(title)
        return lines
