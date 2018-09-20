from flask import redirect, send_from_directory

from zodiwiki.app import app
from zodiwiki.__data__ import *


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder,
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/page/<string:name>')
def page(name):
    wiki = app.config['wiki']
    if name not in wiki:
        return 'no page or tag found with name ' + name, 404
    page, sub_pages = wiki[name]
    ret = ''
    if page:
        ret += page.html
    else:
        ret += f'<h1 id="{name}">{name}</h1>'

    if sub_pages:
        ret += '<u>Pages referenced by this tag:</u><ul>'
        for sp in sub_pages:
            ret += f'<li><a href="{wiki.linkto(sp)}">{sp.title}</a></li>'
        ret += '</ul>'

    if page and page.tags:
        ret += '<u>This page has the tags:</u><ul>'
        for t in page.tags:
            ret += f'<li><a href="{wiki.linkto(t)}">{t}</a></li>'
        ret += '</ul>'

    return ret


@app.route('/all')
def list_pages():
    wiki = app.config['wiki']
    ret = '<u>The following pages are defined in the wiki:</u><ul>'
    for title, page in wiki.pages.items():
        ret += f'<li><a href="{wiki.linkto(page)}">{title}</a></li>'
    ret += '</ul>'
    ret += '<u>The following tags are defined in the wiki:</u><ul>'
    for tag_name in wiki.tags:
        ret += f'<li><a href="{wiki.linkto(tag_name)}">{tag_name}</a></li>'
    ret += '</ul>'
    return ret


@app.route('/')
def index():
    wiki = app.config['wiki']
    if 'index' in wiki:
        return redirect(wiki.linkto('index'))
    return redirect('/all')


@app.route('/match/<string:main>/')
@app.route('/match/<string:main>/<string:hints>')
def matches(main, hints=''):
    wiki = app.config['wiki']
    matches = sorted(wiki.match(main, hints), key=lambda x: x[-1], reverse=True)
    ret = '<u>The following pages matched:</u><ul>'
    for page, score in matches:
        if score == 0:
            break
        ret += f'<li><a href="{wiki.linkto(page)}">{page.title} (score: {score})</a></li>'
    ret += '</ul>'
    return ret


@app.route('/bestmatch/<string:main>/')
@app.route('/bestmatch/<string:main>/<string:hints>')
def best_match(main, hints=''):
    wiki = app.config['wiki']
    best = wiki.best_match(main, hints)
    return redirect(best.linkto)

# todo template? icon?
# todo about
