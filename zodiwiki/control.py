from typing import Dict, Any
import webbrowser
from functools import partial
from textwrap import wrap, dedent
import os
from pathlib import Path


class Controller(Dict[str, Any]):
    def __init__(self):
        super().__init__()
        self.docs: Dict[str, str] = {}
        self.register(help_, self)

    def __setitem__(self, key, value):
        raise Exception('items can only be set using the register method')

    def register(self, item, *args, _name=None, _doc=..., **kwargs):
        if _name is None:
            _name = getattr(item, '__name__', str(item)).rstrip('_')
        if _doc is ...:
            _doc = item.__doc__
        if args or kwargs:
            item = partial(item, *args, **kwargs)
        super().__setitem__(_name, item)
        if _doc is not None:
            self.docs[_name] = _doc


def help_(controller: Controller):
    """show help message for the controller"""
    ret = []
    for k, v in sorted(controller.docs.items(), key=lambda x:x[0]):
        ret.append(k + ':')
        ret.extend(wrap(dedent(v).strip(), 120, initial_indent='\t', subsequent_indent='\t'))
    print('\n'.join(ret))


def quit_(*to_close):
    """
    close the exec and exit
    """
    for tc in to_close:
        tc.close()
    exit()


def rescan(wiki, show_warnings=True):
    """re-scan the wiki directory and show the ref warnings (note, does not update the html templates)"""
    wiki.scan_path(clear=True)
    if show_warnings:
        show_ref_warnings(wiki)


def show_(server):
    """open a browser window to the wiki"""
    url = server.url()
    webbrowser.open(url)


def show_ref_warnings(wiki):
    """display ref broken links and orphan pages, preload the refs if necessary"""
    if wiki.ref_info is None:
        wiki.preload_refs()
    for p, ri in wiki.ref_info.items():
        if not ri.links_in:
            print('orphan page: ' + p.title)
        for r, bads in ri.bad_links.items():
            for b in bads:
                print(f'bad link in {p.title}: {b} ({r})')


def show_directory(wiki):
    """open the wiki root directory"""
    os.startfile(wiki.root_dir_path)


def show_file(wiki, path):
    """opens a file in the wiki directory"""
    p: Path = (wiki.root_dir_path / path)
    try:
        if p.exists():
            print('opening ' + str(p))
            os.startfile(p)
            return
    except OSError:
        pass

    i = iter(wiki.root_dir_path.rglob(path))
    f = next(i, None)
    if f is None:
        print('no files matching pattern ' + path)
        return
    if next(i, None) is not None:
        print('multiple files matching pattern ' + path)
        return
    print('opening ' + str(f))
    os.startfile(f)


def show_page(wiki, main, hints=''):
    """open a specific wiki page"""
    cands = wiki.best_match(main, hints)
    if len(cands) > 1:
        print('multiple candidates, enter the number of the correct page:')
        for i, (score, page) in enumerate(cands):
            print(f'[{i}]\t{page.title}({score}) @ {page.path}')
        while True:
            inp = input('enter a number, or nothing to cancel: ')
            if not inp:
                return 'cancelled'
            if not inp.isnumeric():
                print('bad input')
                continue
            page = cands[int(inp)]
            break
    else:
        if cands.cuton <= wiki.best_match_min:
            print('warning: matches has low score')
        page = cands.best_key()

    if not page.path:
        return 'selected page cannot be opened, it has no path'

    print('opening ' + str(page.path))
    os.startfile(page.path)

# todo create file?
# todo open root directory
