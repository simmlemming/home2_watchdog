from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import im.myhome.log as log
import im.myhome.storage as storage
from urllib.parse import urlparse, parse_qs


class UploadImageHandler(BaseHTTPRequestHandler):

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path.startswith('/p'):
            code, picture, message = self.__get_picture()
        else:
            code, picture, message = HTTPStatus.NOT_FOUND, None, 'Unknown path: ' + self.path

        if picture:
            self.__send_bytes(code, picture, content_type='image/jpeg')
        else:
            self.__send(code, message, content_type='text/plain')

    # curl -H "Content-Type: image/jpeg" --data-binary @"./cat.jpg" http://127.0.0.1:8080/p/1
    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path.startswith('/p/'):  # TODO: use regex to match '/p/[0-9]+'
            code, message, path = self.__save_picture()
        else:
            code, message = HTTPStatus.NOT_FOUND, 'Unknown path: ' + self.path

        self.__send(code, message, content_type='text/plain')

    def __get_picture(self):
        query_str = urlparse(self.path).query
        query = parse_qs(query_str)

        filename = query.get('filename')
        if filename and len(filename) > 0:
            try:
                picture = storage.get_picture_by_name(filename[0])
                return HTTPStatus.OK, picture, None
            except Exception as e:
                return HTTPStatus.INTERNAL_SERVER_ERROR, None, str(e)

        return HTTPStatus.BAD_REQUEST, None, 'No file name'

    def __save_picture(self):
        path_segments = self.path.split('/')

        if len(path_segments) < 3:
            return HTTPStatus.BAD_REQUEST, 'No camera index in the path', None

        camera_index = path_segments[2]
        if not camera_index:
            return HTTPStatus.BAD_REQUEST, 'No camera index in the path', None

        mime_type = self.headers['Content-Type']
        if mime_type != 'image/jpeg':
            return HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Only image/jpeg is supported", None

        length = self.headers['content-length']
        picture = self.rfile.read(int(length))

        try:
            path = storage.save_picture(camera_index, picture)
        except Exception as e:
            return HTTPStatus.INTERNAL_SERVER_ERROR, str(e), None

        return HTTPStatus.OK, 'OK', path

    def __send_bytes(self, code, body, content_type='text/json'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(body)

    def __send(self, code, message, content_type='text/json'):
        self.__send_bytes(code, bytes(message, encoding='utf8'), content_type)

        log.d(message)
        if code != HTTPStatus.OK:
            log.e('%s: %s' % (code, message))
