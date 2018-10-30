import flask

import zodiwiki.__data__ as data

app = flask.Flask('zodiwiki')
app.config.update(
    prog=f'{data.__name__} v{data.__version__}',
    author=data.__author__,
    src_page=data.__homepage__
)
