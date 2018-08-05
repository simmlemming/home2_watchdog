import paho.mqtt.client as mqtt
import im.myhome.log as log
import json
import time
from threading import Thread

from im.myhome.config_local import mqtt_username, mqtt_password, mqtt_port, mqtt_url

NAME = "control_center"
CHANNEL_OUT = "home/out"
CHANNEL_IN = "home/in"
COLLECTING_SENSORS_TIME_SEC = 3

is_collecting_sensors = False
sensors = dict()


def on_connect(client, userdata, flags, rc):
    log.i("Connected with result code " + str(rc))
    (_, mid) = client.subscribe("home/out")
    log.i("Subscribing " + str(mid))


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


def on_subscribe(client, userdata, mid, granted_qos):
    log.i("Subscribed " + str(mid))
    start_collecting_sensors(client)


def stop_collecting_sensors():
    time.sleep(COLLECTING_SENSORS_TIME_SEC)
    global is_collecting_sensors
    is_collecting_sensors = False
    log.i("Stopped collecting sensors, got " + str(len(sensors)))
    for s in sensors:
        log.i("    " + s)


def start_collecting_sensors(client):
    global is_collecting_sensors
    is_collecting_sensors = True

    cmd = dict(name='all', cmd='state')
    client.publish(CHANNEL_IN, json.dumps(cmd))

    # scheduler.enter(10, 1, stop_collecting_sensors)
    # scheduler.run(blocking=False)

    t = Thread(target=stop_collecting_sensors)
    t.start()

    log.i("Started collecting sensors")


def on_message(message):
    # log.i(str(message))
    global sensors
    global is_collecting_sensors

    if is_collecting_sensors:
        sensors[message['name']] = message['type']
        log.i("sensors count = " + str(len(sensors)))


def publish_debug(client, error_message):
    client.publish("home/debug", error_message)


log.init()

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(mqtt_username, mqtt_password)
mqtt_client.on_connect = on_connect
mqtt_client.on_subscribe = on_subscribe
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect(mqtt_url, mqtt_port, 60)
mqtt_client.loop_forever()
