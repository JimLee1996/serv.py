import os
import posixpath
import sys
import urllib.parse
import argparse

from http.server import HTTPServer, SimpleHTTPRequestHandler


class JimHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Rewrite method translate_path() to support assignment of specific root_dir.
    """

    def translate_path(self, path):

        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        # modify path instead of path = os.getcwd() to support arbitrary dir.
        path = self.server.root_dir
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path


class JimHTTPServer(HTTPServer):
    """ Rewrite class HTTPServer to support passing in root_dir
    """

    def __init__(
        self,
        root_dir,
        server_address,
        RequestHandlerClass=JimHTTPRequestHandler
    ):
        self.root_dir = root_dir
        HTTPServer.__init__(self, server_address, RequestHandlerClass)


def run(
    root_dir='web',
    port=8000,
    bind="",
    HandlerClass=JimHTTPRequestHandler,
    ServerClass=JimHTTPServer,
    protocol="HTTP/1.0",
):
    server_address = (bind, port)
    print(port)

    HandlerClass.protocol_version = protocol

    httpd = ServerClass(root_dir, server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
    print(serve_message.format(host=sa[0], port=sa[1]))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A Simple Web Server.")
    parser.add_argument(
        '-d',
        '--dir',
        default='web',
        help='Specify alternate dir [default: web]'
    )
    parser.add_argument(
        '-p',
        '--port',
        default=8000,
        type=int,
        help='Specify alternate port [default: 8000]'
    )
    parser.add_argument(
        '-b',
        '--bind',
        default='',
        metavar='ADDRESS',
        help='Specify alternate bind address '
        '[default: all interfaces]'
    )
    args = parser.parse_args()

    run(args.dir, args.port, args.bind)
