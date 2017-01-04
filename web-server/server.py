# -*- coding: utf-8 -*-

import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class BaseCase(object):
    def file_handler(self, handler, path, model='r'):
        try:
            with open(path, model) as f:
                content = f.read()
                if not isinstance(content, bytes):
                    content = content.encode('utf-8')
                handler.send_content(content)
        except IOError as e:
            raise ServerException(e)

    # must method test and act
    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'

class CaseNoPathExist(BaseCase):
    def test(self, handler):
        """

        :type handler: Handler instance
        """
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        message = 'the path {} not exist'.format(handler.full_path)
        raise ServerException(message)


class CaseNotFile(BaseCase):
    def test(self, handler):
        return not os.path.isfile(handler.full_path)

    def act(self, handler):
        message = '{} not a file'.format(handler.full_path)
        raise ServerException(message)


class CaseStaticFile(BaseCase):
    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.html')

    def act(self, handler):
        self.file_handler(handler, handler.full_path, 'rb')


class CaseRootDir(BaseCase):
    def test(self, handler):
        return handler.path == '/' and 'index.html' in \
                                       os.listdir(os.path.abspath(os.path.dirname(__name__)))

    def act(self, handler):
        path = os.path.join(handler.full_path, 'index.html')
        self.file_handler(handler, path, 'rb')


class CaseCGIFile(BaseCase):
    def test(self, handler):
        return handler.full_path.endswith('.py')

    def act(self, handler):
        import subprocess
        child = subprocess.check_output(['python', handler.full_path],
                                        universal_newlines=True)
        return handler.send_content(child.encode('utf-8'))


class RequestHandler(BaseHTTPRequestHandler):

    # Note the sort
    request_cases = [
        CaseRootDir(),        # first condition
        CaseNoPathExist(),
        CaseNotFile(),
        CaseCGIFile(),
        CaseStaticFile()
    ]

    def do_GET(self):
        try:
            basedir = os.path.abspath(os.path.dirname(__file__))
            # only for windows
            file_name = self.path.lstrip('/').replace('/', '\\')
            self.full_path = os.path.join(basedir, file_name)

            for case in self.request_cases:
                if case.test(self):
                    case.act(self)
                    break

        except Exception as e:
            self.handle_error(e)


    def handle_error(self, e):
        page = '''\
        <html><body>
        <h>Error</h>
        <p>{0}</p>
        </body></html>
        '''
        self.send_content(page.format(e).encode('utf-8'), 404)

    def send_content(self, page, status=200):
        # page is must byte
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)


class ServerException(Exception):
    """internal server exception"""
    pass


if __name__ == "__main__":
    serverAddress = ('', 8000)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
