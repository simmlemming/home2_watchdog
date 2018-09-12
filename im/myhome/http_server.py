from http.server import HTTPServer
import im.myhome.log as log
from im.myhome.http_handlers.upload_image import UploadImageHandler
# from org.home.server.request_handler import HomeRequestHandler
import signal
import threading
import getopt
import sys


server = None


def shutdown_server(signal, frame):
    log.i('*** Shutting down (killed) ***')
    if server:
        threading.Thread(daemon=True, target=server.shutdown).start()


def get_ip_from_args():
    opts, args = getopt.getopt(sys.argv[1:], "a:")

    for opt, arg in opts:
        if opt == "-a":
            return arg

    print('You can set an ip address by passing -a parameter: ... -a 127.0.0.1')
    return '0.0.0.0'


def main():
    global server

    ip_address = get_ip_from_args()
    ip_port = 8080

    log.init()
    signal.signal(signal.SIGTERM, shutdown_server)

    server = HTTPServer((ip_address, ip_port), UploadImageHandler)
    log.i('*** Started on {0}:{1} ***'.format(ip_address, ip_port))

    try:
        # Wait forever for incoming http requests
        server.serve_forever()

    except KeyboardInterrupt:
        log.i('Shutting down (^C received)')
        server.socket.close()


if __name__ == '__main__':
    main()
