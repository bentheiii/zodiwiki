import argparse
from pathlib import Path
from io import StringIO
import re

parser = argparse.ArgumentParser()

parser.add_argument('root', type=Path)

sentence_char = r'[a-zA-Z.0-9,?]'

preview_range = 20
pattern = re.compile(fr'({sentence_char})(\n\r?)+({sentence_char})')


def main():
    args = parser.parse_args()
    root: Path = args.root
    assert root.is_dir()
    for file in root.iterdir():
        content = file.read_text()
        write_buffer = StringIO()
        i = 0
        changes = 0
        while i < len(content):
            answer = ''
            breaker = pattern.match(content, i)
            if breaker:
                pre_break = breaker[1]
                post_break = breaker[3]
                answer = 'y'

            if answer != '':
                write_buffer.write(pre_break + ' ' + post_break)
                i += len(breaker[0])
                changes += 1
            else:
                word_to_digest = content[i]
                write_buffer.write(word_to_digest[0])
                i += len(word_to_digest[0])
        if changes:
            file.write_text(write_buffer.getvalue())


if __name__ == '__main__':
    main()
