from flask import redirect, send_from_directory, render_template, request

from zodilib import Wiki

from zodiwiki.app import app

BEST_MATCH_MIN = 5


def w() -> Wiki:
    return app.config['wiki']


def query_for(main, hint):
    if hint:
        return '{' + main + '| ' + hint + '}'
    return '{' + main + '}'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder,
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/page/<string:name>')
def page(name):
    wiki = w()
    name = name.lower()
    if name not in wiki:
        return 'no page or tag found with name ' + name, 404
    page, sub_pages = wiki[name]
    sp_titles = sorted(((wiki.link_to(p), p.title) for p in sub_pages), key=lambda x: x[1]) if sub_pages else ()
    return render_template('article.html', page=page, sp_titles=sp_titles)


@app.route('/all')
def all_pages():
    wiki = w()
    titles = [(p.link_to, t, p.title) for p in wiki.unique_pages for t in p.titles]
    titles.sort(key=lambda x: x[1].lower())
    tags = [(wiki.link_to(t), t) for t in wiki.tags]
    tags.sort(key=lambda x: x[1])
    return render_template('all_pages.html', articles=titles, tags=tags)


@app.route('/')
def index():
    wiki = w()
    if 'index' in wiki:
        return redirect(wiki.link_to('index'))
    return redirect('/all')

@app.route('/match')
def matches_request():
    main = request.args['main']
    hints = request.args.get('hints', '')
    return matches(main, hints)

@app.route('/match/<string:main>/')
@app.route('/match/<string:main>/<string:hints>')
def matches(main, hints=''):
    wiki = w()
    matches = sorted(wiki.match(main, hints), key=lambda x: x[-1], reverse=True)
    pages = []
    for page, score in matches:
        if score == 0:
            break
        pages.append((wiki.link_to(page), page.title, score))
    return render_template('matches.html', pages=pages, query=query_for(main, hints))


@app.route('/bestmatch')
def best_match_request():
    main = request.args['main']
    hints = request.args.get('hints', '')
    return best_match(main, hints)

@app.route('/bestmatch/<string:main>/')
@app.route('/bestmatch/<string:main>/<string:hints>')
def best_match(main, hints=''):
    wiki = w()
    bests = wiki.best_match(main, hints)

    candidates = ((wiki.link_to(page), page.title, score) for (score, page) in bests)

    if bests.cuton <= BEST_MATCH_MIN:
        return render_template('bad_match.html', pages=candidates, query=query_for(main, hints), reason='bad')

    if len(bests) == 1:
        return redirect(bests.best_key().link_to)

    return render_template('bad_match.html', pages=candidates, query=query_for(main, hints), reason='ambiguous')


@app.route('/rsc/<path:file>')
def rsc(file):
    wiki = w()
    return send_from_directory(wiki.rsc_dir_path, file)


@app.route('/src')
@app.route('/src/<path:path>')
def src(path=''):
    return redirect(app.config['src_page'] + path)


@app.route('/about')
def about():
    return render_template('about.html')

# todo create file?
# todo pre-generate all the links?
