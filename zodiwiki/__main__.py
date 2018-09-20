import argparse

from zodilib import Wiki

from zodiwiki import app

parser = argparse.ArgumentParser('zodiwiki')
parser.add_argument('path', help='path to the wiki directory')

def main(args=None):
    args = parser.parse_args(args)

    wiki = Wiki.from_dir(args.path)
    app.config['wiki'] = wiki

    app.run()


if __name__ == '__main__':
    main()
