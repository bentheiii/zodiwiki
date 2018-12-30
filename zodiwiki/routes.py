from flask import redirect, send_from_directory, render_template, request, Markup

from zodilib import Wiki

from zodiwiki.app import app
from zodiwiki.control import rescan
from zodiwiki.__util__ import *


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
    return render_template('article.html.j2', page=page, sp_titles=sp_titles)


@app.route('/all')
def all_pages():
    wiki = w()
    titles = [(p.link_to, p.title) for p in wiki.unique_pages]
    titles.sort(key=lambda x: x[1].lower())
    tags = [(wiki.link_to(t), t) for t in wiki.tags]
    tags.sort(key=lambda x: x[1])
    return render_template('all_pages.html.j2', articles=titles, tags=tags)


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
    return render_template('matches.html.j2', pages=pages, query=query_for(main, hints))


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

    if bests.cuton <= wiki.best_match_min:
        return render_template('bad_match.html.j2', pages=candidates, query=query_for(main, hints), reason='weak')

    if len(bests) == 1:
        return redirect(bests.best_key().link_to)

    return render_template('bad_match.html.j2', pages=candidates, query=query_for(main, hints), reason='ambiguous')


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
    return render_template('about.html.j2')


@app.route('/preview', methods=['POST'])
def preview():
    md = request.form['md']
    wiki = w()
    http = Markup(wiki.md.convert(md))
    return http


@app.route('/edit')
@app.route('/edit/<string:filename>')
def edit(filename=''):
    if not is_local(request.url):
        return 'only accessible from local', 400
    filedata = ''
    if filename:
        if filename.endswith('.md'):
            filename = filename[:-len('.md')]
        wiki = w()
        dst_path = (wiki.root_dir_path / filename).with_suffix('.md')
        page = wiki.by_path.get(dst_path, None)
        if page:
            filedata = page.md

    return render_template('edit.html.j2', filename=filename, filedata=filedata)


@app.route('/submit_edit', methods=['POST'])
def submit_edit():
    if not is_local(request.url):
        return 'only accessible from local', 400

    wiki = w()
    src_filename = request.form['srcfilename']
    dst_filename = request.form['dstfilename']

    src_path = (wiki.root_dir_path / src_filename).with_suffix('.md')
    dst_path = (wiki.root_dir_path / dst_filename).with_suffix('.md')

    overwrite = request.form.get('overwriteflag', src_path == dst_path)
    clone = request.form.get('cloneflag', False)

    if dst_path.exists():
        if not overwrite:
            return redirect('/')
        backup(dst_path)

    newmd: str = request.form['usermd']
    with dst_path.open('w', newline='') as writer:
        writer.write(newmd)

    if not clone and (src_path != dst_path):
        backup(src_path)

    rescan(wiki)
    page = wiki.by_path.get(dst_path, None)
    if not page:
        return redirect('/')
    return redirect(page.link_to)
