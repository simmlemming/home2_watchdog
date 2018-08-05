import paho.mqtt.client as mqtt
import im.myhome.log as log
import json
import time
from threading import Thread

from im.myhome.config import mqtt_username, mqtt_password, mqtt_port, mqtt_url

NAME = "control_center"
CHANNEL_OUT = "home/out"
CHANNEL_IN = "home/in"

CMD_OFF = "off"
CMD_ON = "on"
CMD_PAUSE = "pause"

TYPE_MOTION_SENSOR = "motion_sensor"

STATE_OFF = 0
STATE_OK = 1
STATE_INIT = 2
STATE_PAUSED = 5

COLLECTING_SENSORS_INTERVAL_SEC = 15
PAUSE_INTERVAL_SEC = 15 * 60  # 15 min
# COLLECTING_SENSORS_INTERVAL_SEC = 4
# PAUSE_INTERVAL_SEC = 4

is_collecting_sensors = False
is_pausing = False
is_resuming = False
sensors = dict()
awaiting_sensors = set()
paused_sensors = set()

subscribe_out_mid = 0


def on_connect(client, userdata, flags, rc):
    global subscribe_out_mid
    (_, subscribe_out_mid) = client.subscribe("home/out")
    client.subscribe("home/in")


def on_mqtt_message(client, userdata, msg):
    msg_str = msg.payload.decode('utf-8')
    # print(msg_str)

    try:
        message = json.loads(msg_str)
        on_message(client, message)
    except json.JSONDecodeError as e:
        error_message = "cannot parse message: " + msg_str + "\n" + str(e)
        log.e(error_message)
        publish_debug(client, error_message)


def on_subscribe(client, userdata, mid, granted_qos):
    if mid == subscribe_out_mid:
        start_collecting_sensors(client)


def stop_collecting_sensors(client):
    time.sleep(COLLECTING_SENSORS_INTERVAL_SEC)
    global is_collecting_sensors
    is_collecting_sensors = False

    sensors_count = len(sensors)
    state_ok = dict(name=NAME, state=STATE_OK, value=sensors_count)
    publish_out(client, state_ok)

    log.i("Stopped collecting sensors, got " + str(sensors_count))


def start_collecting_sensors(client):
    global is_collecting_sensors
    is_collecting_sensors = True

    state_init = dict(name=NAME, state=STATE_INIT)
    publish_out(client, state_init)

    state_cmd = dict(name='all', cmd='state')
    publish_in(client, state_cmd)

    t = Thread(target=stop_collecting_sensors, args=[client])
    t.start()

    log.i("Started collecting sensors")


def start_pause(client):
    global awaiting_sensors, is_pausing
    awaiting_sensors = {s_name for s_name, s_type in sensors.items() if s_type == TYPE_MOTION_SENSOR}
    log.i("pausing sensors: " + str(awaiting_sensors))

    is_pausing = True
    for s in awaiting_sensors:
        off_cmd = dict(name=s, cmd=CMD_OFF)
        publish_in(client, off_cmd)


def on_message(client, message):
    # log.i(str(message))
    global sensors, is_collecting_sensors, is_pausing, paused_sensors

    sensor_name = message.get('name', None)
    sensor_type = message.get('type', None)
    cmd = message.get('cmd', None)
    sensor_state = message.get('state', None)

    if sensor_name is None:
        return

    if is_collecting_sensors and sensor_name is not None and sensor_type is not None:
        sensors[sensor_name] = sensor_type
        log.i("+ " + sensor_name + " [" + str(len(sensors)) + "]")

    if sensor_name == NAME and cmd == CMD_PAUSE:
        start_pause(client)

    if is_pausing and sensor_state == STATE_OFF:
        log.i("GOT response: " + sensor_name + " is off")
        if sensor_name in awaiting_sensors:
            awaiting_sensors.discard(sensor_name)
            paused_sensors.add(sensor_name)

        if len(awaiting_sensors) == 0:
            on_all_paused(client)

    if is_resuming and sensor_state == STATE_OK:
        log.i("GOT response: " + sensor_name + " is on")
        if sensor_name in awaiting_sensors:
            awaiting_sensors.discard(sensor_name)
            paused_sensors.discard(sensor_name)

        if len(awaiting_sensors) == 0:
            on_all_resumed(client)


def on_all_resumed(client):
    global is_resuming
    state = dict(name=NAME, state=STATE_OK)
    publish_out(client, state)
    is_resuming = False


def on_all_paused(client):
    global is_pausing
    state = dict(name=NAME, state=STATE_PAUSED, value=PAUSE_INTERVAL_SEC)
    publish_out(client, state)
    is_pausing = False

    Thread(target=resume_all_paused, args=[client]).start()


def resume_all_paused(client):
    global is_resuming
    time.sleep(PAUSE_INTERVAL_SEC)

    is_resuming = True
    for s_name in paused_sensors:
        on_cmd = dict(name=s_name, cmd=CMD_ON)
        publish_in(client, on_cmd)
        awaiting_sensors.add(s_name)


def publish_in(client, message):
    log.i("> IN " + json.dumps(message))
    client.publish(CHANNEL_IN, json.dumps(message))


def publish_out(client, message):
    log.i("> OUT " + json.dumps(message))
    client.publish(CHANNEL_OUT, json.dumps(message))


def publish_debug(client, error_message):
    client.publish("home/debug", error_message)


# def call_start_pause():
#     log.i('a, start')
#     time.sleep(5)
#     log.i('a, after sleep')
#     start_pause(mqtt_client)


log.init()

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(mqtt_username, mqtt_password)
mqtt_client.on_connect = on_connect
mqtt_client.on_subscribe = on_subscribe
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect(mqtt_url, mqtt_port, 60)

# tt = Thread(target=call_start_pause)
# tt.start()

mqtt_client.loop_forever()
