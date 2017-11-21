import paho.mqtt.client as mqtt
import im.myhome.log as log
import im.myhome.notifier as notifier
import im.myhome.storage as storage
import json
from sqlite3 import OperationalError

from im.myhome.config import mqtt_username, mqtt_password, mqtt_port, mqtt_url


def on_connect(client, userdata, flags, rc):
    log.i("Connected with result code " + str(rc))
    client.subscribe("home/out")


def on_mqtt_message(client, userdata, msg):
    msg_str = msg.payload.decode('utf-8')
    # print(msg_str)

    try:
        message = json.loads(msg_str)
        on_message(message)
    except json.JSONDecodeError as e:
        error_message = "cannot parse message: " + msg_str + "\n" + str(e)
        log.e(error_message)
        publish_debug(client, error_message)


def on_message(message):
    if message.get('state') == 4:
        log.i("alarm!")
        notifier.notify(json.dumps(message))

    if message.get('cmd') == 'add_device':
        try:
            device = message['device']
            log.i("Adding device: " + str(device))
            storage.add_device(device)
        except (OperationalError, KeyError) as e:
            log.e("Cannot add device " + str(message) + " " + str(e))


def publish_debug(client, error_message):
    client.publish("home/debug", error_message)


log.init()

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(mqtt_username, mqtt_password)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_mqtt_message

mqtt_client.connect(mqtt_url, mqtt_port, 60)

mqtt_client.loop_forever()
