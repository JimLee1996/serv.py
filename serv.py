import html
import io
import os
import posixpath
import sys
import urllib.parse
import argparse

from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler


class JimHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Rewrite method translate_path() to support assignment of specific root_dir.
    """

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND, "No permission to list directory"
            )
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(
                self.path, errors='surrogatepass'
            )
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % displaypath
        r.append(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
            '"http://www.w3.org/TR/html4/strict.dtd">'
        )
        r.append('<html>\n<head>')
        r.append(
            '<meta http-equiv="Content-Type" '
            'content="text/html; charset=%s">' % enc
        )
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<ul>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append(
                '<li><a href="%s">%s</a></li>' % (
                    urllib.parse.quote(linkname, errors='surrogatepass'),
                    html.escape(displayname, quote=False)
                )
            )
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

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
