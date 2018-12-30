from typing import Iterable

import argparse
from pathlib import Path
from io import StringIO
from itertools import islice
import re

from zodilib import Wiki

from tools.trie import Trie

parser = argparse.ArgumentParser()

parser.add_argument('root', type=Path)


def merge_keys(d: dict, *keys: str) -> Iterable[str]:
    ret = []
    for k in keys:
        ret.extend(d.get(k, ()))
    return ret


preview_range = 20
word_sep_pattern = re.compile(r'({[^}]})|([a-zA-Z0-9]*([^a-zA-Z0-9]|$))')


def main():
    args = parser.parse_args()
    root: Path = args.root
    title_dict: Trie[str, Path] = Trie()  # maps lowercase titles to their file path
    md_parser = Wiki.Default_MD
    assert root.is_dir()
    for file in root.iterdir():
        md_parser.convert(file.read_text())
        meta = md_parser.Meta
        md_parser.reset()
        # todo use an extension to generate the titles in the markdown
        titles = merge_keys(meta, 'title', 'titles', 'alias', 'aliases')
        for title in titles:
            if title_dict.setdefault(title.lower(), file) != file:
                raise Exception(f'duplicate title: {title} at {file} and {title_dict[title]}')

    for file in root.iterdir():
        prefix_blacklist = {None}
        content = file.read_text()
        write_buffer = StringIO()
        i = 0
        changes = 0
        while i < len(content):
            answer = ''
            slice_ = islice(content, i, None)
            prefix = title_dict.longest_prefix(c.lower() for c in slice_)
            if prefix not in prefix_blacklist and title_dict[prefix] != file:
                lower_bound = max(0, i - preview_range)
                upper_bound = min(i + len(prefix) + preview_range, len(content))
                preview_pre = content[lower_bound: i]
                preview_post = content[i + len(prefix):upper_bound]
                answer = input(
                    f"@{file} (char {i}): ...{preview_pre + prefix + preview_post!r}...->{preview_pre + '{' + prefix + '}' + preview_post!r}?")
                if not answer:
                    prefix_blacklist.add(prefix)

            if answer != '':
                write_buffer.write('{' + prefix + '}')
                i += len(prefix)
                changes += 1
            else:
                word_to_digest = word_sep_pattern.match(content, i)
                write_buffer.write(word_to_digest[0])
                i += len(word_to_digest[0])
        if changes:
            file.write_text(write_buffer.getvalue())


if __name__ == '__main__':
    main()
