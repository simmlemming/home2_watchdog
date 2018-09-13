import paho.mqtt.client as mqtt
import requests
import getopt
import sys
from http import HTTPStatus
from im.myhome.config import mqtt_username, mqtt_password, mqtt_port, mqtt_url


def parse_args():
    opts, args = getopt.getopt(sys.argv[1:], "f:c:")

    camera_index = None
    file_name = None

    for opt, arg in opts:
        if opt == "-c":
            camera_index = arg
        elif opt == "-f":
            file_name = arg

    return camera_index, file_name


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def main():
    camera_index, file_name = parse_args()

    if not file_name:
        print('File not found in arguments (-f)')
        exit(1)

    if not camera_index:
        print('Camera index not found in arguments (-c)')
        exit(1)

    print('Uploading ' + file_name)

    with open(file_name, 'rb') as f:
        r = requests.post('http://127.0.0.1:8080/p/' + camera_index, data=f.read(), headers={'Content-Type': 'image/jpeg'})

    print(r.status_code)
    print(r.content)

    if r.status_code != HTTPStatus.OK:
        exit(1)

    try:
        response = r.json()
        file_name = response.get('filename')
        print('Uploaded file name: ' + file_name)

        mqtt_client = mqtt.Client()
        mqtt_client.username_pw_set(mqtt_username, mqtt_password)
        mqtt_client.on_connect = on_connect

        # mqtt_client.connect(mqtt_url, mqtt_port, 60)
        # dict(name='camera_' + camera_index, value=)
        # mqtt_client.publish(topic='home/out', payload=)
        #
        # mqtt_client.loop_start()
    except ValueError as e:
        print('Cannot parse response: ' + str(e))


if __name__ == '__main__':
    main()
