from typing import Dict, Any
import webbrowser
from functools import partial
from textwrap import wrap, dedent


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
    for k, v in controller.docs.items():
        ret.append(k + ':')
        ret.extend(wrap(dedent(v).strip(), 120, initial_indent='\t', subsequent_indent='\t'))
    print('\n'.join(ret))


def quit_(*to_close):
    """
    close the server and exit
    """
    for tc in to_close:
        tc.close()
    exit()


def show_(server):
    """open a browser window to the wiki"""
    url = server.url()
    webbrowser.open(url)

# todo reload config
# todo reload pages?
