import argparse
from threading import Thread
import time

from pyfladesk import init_gui
from gevent.pywsgi import WSGIServer

from zodilib import Wiki

from zodiwiki import app
from zodiwiki import control

parser = argparse.ArgumentParser('zodiwiki', add_help=False)
parser.add_argument('mode', choices=('web', 'desktop'))
parser.add_argument('path', help='path to the wiki directory')

parser.add_argument('-h', '--host', type=str, help='host name', dest='host', required=False, default='localhost')
parser.add_argument('-p', '--port', type=int, help='binding port', dest='port', required=False, default=5000)
parser.add_argument('--preload', type=str, help='whether to preload reference links in the wiki',
                    dest='preload', choices=('no', 'yes', 'warn'), required=False, default='warn')

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


class DesktopThread(Thread):
    def __init__(self, *args, port, app, wiki, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = port
        self.app = app
        self.wiki = wiki
        self.exec = None

    def run(self):
        self.exec = init_gui(self.app, port=self.port, window_title=self.wiki.title, argv=[],
                             height=600, width=800)


def main(args=None):
    args = parser.parse_args(args)

    mode = args.mode

    wiki = Wiki.from_dir(args.path, preload=args.preload != 'no')
    if args.preload == 'warn':
        control.show_ref_warnings(wiki)

    app.config['wiki'] = wiki

    command_dict = control.Controller()
    command_dict.register(wiki, _name='wiki', _doc='the main wiki object')

    if mode == 'web':
        server_thread = ServerThread(port=args.port, app=app, host=args.host)
        server_thread.start()
        print('@ ' + server_thread.url())
        command_dict.register(control.quit_, server_thread)
        command_dict.register(control.show_, server_thread)
    elif mode == 'desktop':
        thread = DesktopThread(port=args.port, app=app, wiki=wiki)
        thread.start()
    print('started!')

    command_dict.register(control.show_ref_warnings, wiki)
    command_dict.register(control.show_directory, wiki)
    command_dict.register(control.show_page, wiki)
    command_dict.register(control.rescan, wiki, show_warnings=bool(args.preload))
    command_dict.register(control.show_file, wiki)

    time.sleep(0.1)

    while True:
        comm = input('>>> ')
        try:
            ret = eval(comm, command_dict)
            if callable(ret):
                ret = ret()
        except (SyntaxError, NameError, TypeError) as e:
            print(e)
        else:
            if ret:
                print(ret)


if __name__ == '__main__':
    main()

# todo multiple dirs?
