# -*- coding: utf-8 -*-
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class CaseNoPathExist(object):
    def test(self, handler):
        """

        :type handler: Handler instance
        """
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        message = 'the path {} not exist'.format(handler.full_path)
        raise ServerException(message)


class CaseNotFile(object):
    def test(self, handler):
        return not os.path.isfile(handler.full_path)

    def act(self, handler):
        message = '{} not a file'.format(handler.full_path)
        raise ServerException(message)


class CaseStaticFile(object):
    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.html')

    def act(self, handler):
        try:
            with open(handler.full_path, 'rb') as f:
                handler.send_content(f.read())
        except IOError as e:
            raise ServerException(e)


class CaseRootDir(object):
    def test(self, handler):
        return handler.path == '/' and 'index.html' in \
                                       os.listdir(os.path.abspath(os.path.dirname(__name__)))

    def act(self, handler):
        with open(os.path.join(handler.full_path, 'index.html'), 'rb') as f:
            handler.send_content(f.read())


class CaseCGIFile(object):
    def test(self, handler):
        return handler.full_path.endswith('.py')

    def act(self, handler):
        import subprocess
        child = subprocess.check_output(['python', handler.full_path],
                                        universal_newlines=True)
        return handler.send_content(child.encode('utf-8'))


class RequestHandler(BaseHTTPRequestHandler):
    page = '''\
        <html>
        <body>
        <table>
        <tr>  <td>Header</td>         <td>Value</td>          </tr>
        <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
        <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
        <tr>  <td>Client port</td>    <td>{client_port}</td> </tr>
        <tr>  <td>Command</td>        <td>{command}</td>      </tr>
        <tr>  <td>Path</td>           <td>{path}</td>         </tr>
        </table>
        </body>
        </html>\
    '''

    # Note the sort
    request_cases = [
        CaseRootDir(),        # first codition
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

            # if not os.path.exists(full_path):
            #     message = '{0} not found'.format(full_path)
            #     raise ServerException(message)
            # elif not os.path.isfile(full_path):
            #     message = '{0} not a file'.format(full_path)
            #     raise ServerException(message)
            #
            # try:
            #     with open(full_path, 'rb') as f:
            #         content = f.read()
            #         self.send_content(content)
            # except Exception as e:
            #     raise ServerException(e)

            for case in self.request_cases:
                if case.test(self):
                    case.act(self)
                    break

        except Exception as e:
            self.handle_error(e)

    # def create_page(self):
    #     values = {
    #         'date_time': self.date_time_string(),
    #         'client_host': self.client_address[0],
    #         'client_port': self.client_address[1],
    #         'command': self.command,
    #         'path': self.path
    #     }
    #     page = self.page.format(**values).encode("utf-8")
    #     return page

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
