import argparse
from pathlib import Path
import re

parser = argparse.ArgumentParser()

parser.add_argument('root', type=Path)

sentence_char = r'[a-zA-Z.0-9,?]'

preview_range = 20


def main():
    pattern = re.compile(input('enter regex pattern:\n'))
    args = parser.parse_args()
    root: Path = args.root
    assert root.is_dir()
    for file in root.iterdir():
        content = file.read_text()
        for match in pattern.finditer(content):
            preview = content[max(match.start(0) - preview_range, 0):
                              min(match.end(0) + preview_range, len(content))]
            print(f"@{file} (char {match.start(0)}): ...{preview!r}...")


if __name__ == '__main__':
    main()
