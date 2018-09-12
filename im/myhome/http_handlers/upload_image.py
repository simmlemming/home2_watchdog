from http.server import BaseHTTPRequestHandler
import im.myhome.log as log
import im.myhome.storage as storage
from http import HTTPStatus


class UploadImageHandler(BaseHTTPRequestHandler):

    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path.startswith('/p/'):  # TODO: use regex to match '/p/[0-9]+'
            code, message, path = self.save_picture()
        else:
            code, message = HTTPStatus.NOT_FOUND, 'Unknown path: ' + self.path

        self.send(code, message, content_type='text/plain')

    def send(self, code, message, content_type='text/json'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(bytes(message, encoding='utf8'))

        log.d(message)
        if code != HTTPStatus.OK:
            log.e('%s: %s' % (code, message))

    def save_picture(self):
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
