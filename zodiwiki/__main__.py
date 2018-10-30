import argparse
from threading import Thread
from functools import partial

from gevent.pywsgi import WSGIServer

from zodilib import Wiki

from zodiwiki import app
from zodiwiki import control

parser = argparse.ArgumentParser('zodiwiki', add_help=False)
parser.add_argument('path', help='path to the wiki directory')

parser.add_argument('-h', '--host', type=str, help='host name', dest='host', required=False, default='localhost')
parser.add_argument('-p', '--port', type=int, help='binding port', dest='port', required=False, default=5000)

parser.add_argument('--help', action='help')

class ServerThread(Thread):
    def __init__(self, *args, port, app, host, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = port
        self.app = app
        self.host = host
        self.server: WSGIServer = None

    def run(self):
        self.server = WSGIServer((self.host, self.port), self.app)
        self.server.serve_forever()

    def close(self):
        self.server.close()

    def url(self):
        return 'http://' + self.host + ':' + str(self.port)


def main(args=None):
    args = parser.parse_args(args)

    wiki = Wiki.from_dir(args.path)
    app.config['wiki'] = wiki

    server_thread = ServerThread(port=args.port, app=app, host=args.host)
    print('starting server...', end='', flush=True)
    server_thread.start()
    print('started!')
    print('@ ' + server_thread.url())

    command_dict = control.Controller()
    command_dict.register(wiki, _name='wiki', _doc='the main wiki object')
    command_dict.register(control.quit_, server_thread)
    command_dict.register(control.show_, server_thread)
    command_dict.register(wiki.scan_path, clear=True, _name='re_scan',
                          _doc='re-scan the wiki directory (note, does not update the html templates)')

    while True:
        comm = input()
        try:
            ret = eval(comm, command_dict)
        except SyntaxError as e:
            print(e)
        else:
            if callable(ret):
                ret = ret()
            if ret:
                print(ret)


if __name__ == '__main__':
    main()

# todo audo-update (both for page and dir content)
# todo multiple dirs?
