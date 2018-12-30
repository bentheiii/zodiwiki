from urllib.parse import urlparse
from pathlib import Path


def is_local(url):
    parsed = urlparse(url)
    if parsed.hostname in ('127.0.0.1', 'localhost'):
        return True
    return False


def backup(path: Path):
    i = 0
    while True:
        trg_path = path.with_suffix('.md.bk.' + str(i))
        if trg_path.exists():
            i += 1
            continue
        path.rename(trg_path)
        return trg_path


__all__ = ['is_local', 'backup']
