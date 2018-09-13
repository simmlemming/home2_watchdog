from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import im.myhome.log as log
import im.myhome.storage as storage
from urllib.parse import urlparse, parse_qs
import json


class PicturesHandler(BaseHTTPRequestHandler):

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path.startswith('/p'):
            code, picture = self.__get_picture()
            self.__send_bytes(code, picture, content_type='image/jpeg')
            return

        self.__send(HTTPStatus.NOT_FOUND, 'Unknown path: ' + self.path, content_type='text/plain')

    # curl -H "Content-Type: image/jpeg" --data-binary @"./cat.jpg" http://127.0.0.1:8080/p/1
    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path.startswith('/p/'):  # TODO: use regex to match '/p/[0-9]+'
            code, message = self.__save_picture()
        else:
            code, message = HTTPStatus.NOT_FOUND, 'Unknown path: ' + self.path

        self.__send(code, message, content_type='text/plain')

    def __get_picture(self):
        filename = self.__get_query_param('filename')
        timestamp = self.__get_query_param('timestamp')
        camera_index = self.__get_query_param('camera_index')

        picture = None
        try:
            if filename:
                picture = storage.get_picture_by_name(filename)
            elif timestamp and camera_index:
                picture = storage.get_picture_by_timestamp(camera_index, timestamp)
        except Exception as e:
            log.e(str(e))
            return HTTPStatus.INTERNAL_SERVER_ERROR, None

        if picture:
            return HTTPStatus.OK, picture

        return HTTPStatus.NOT_FOUND, None

    def __get_query_param(self, key):
        query_str = urlparse(self.path).query
        query = parse_qs(query_str)

        value = query.get(key)
        if value and len(value) > 0:
            return value[0]

        return None

    def __save_picture(self):
        path_segments = self.path.split('/')

        if len(path_segments) < 3:
            return HTTPStatus.BAD_REQUEST, 'No camera index in the path'

        camera_index = path_segments[2]
        if not camera_index:
            return HTTPStatus.BAD_REQUEST, 'No camera index in the path'

        mime_type = self.headers['Content-Type']
        if mime_type != 'image/jpeg':
            return HTTPStatus.UNSUPPORTED_MEDIA_TYPE, 'Only image/jpeg is supported, was ' + mime_type

        length = self.headers['content-length']
        picture = self.rfile.read(int(length))

        try:
            file_name = storage.save_picture(camera_index, picture)
            body = dict(filename=file_name)
            return HTTPStatus.OK, json.dumps(body)
        except Exception as e:
            log.e(str(e))
            return HTTPStatus.INTERNAL_SERVER_ERROR, str(e)

    def __send_bytes(self, code, body, content_type='text/json'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def __send(self, code, message, content_type='text/json'):
        self.__send_bytes(code, bytes(message, encoding='utf8'), content_type)

        log.d(message)
        if code != HTTPStatus.OK:
            log.e('%s: %s' % (code, message))
