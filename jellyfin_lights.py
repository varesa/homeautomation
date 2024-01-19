import paho.mqtt.client as mqtt
from time import sleep
import json
import random
from traceback import print_exc
import jellyfin

DEVICES_TOPIC = 'zigbee2mqtt/bridge/devices'

lamps = set()
events = []
action = ""

def on_connect(client, userdata, flags, rc):
    print("Connected")


def on_message(client, userdata, message):
    if message.topic == DEVICES_TOPIC:
        print("Got devices")
        devices = json.loads(message.payload)
        for device in devices:
            definition = device['definition']
            if definition and ('LED' in definition.get('model', '') or '9290011370' in definition.get('model', '')):
                lamps.add(device['friendly_name'])
        print("lamps:", lamps)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost')
client.subscribe(DEVICES_TOPIC)
client.loop_start()


def set_lamp(lamp: str, state: str):
    client.publish('zigbee2mqtt/' + lamp + '/set', '{"state": "' + state + '"}')

def set_brightness(lamp: str, state: str):
    client.publish('zigbee2mqtt/' + lamp + '/set', '{"brightness": "' + state + '"}')


def set_lamp_prefixes(lamp_prefixes: list[str], state: str):
    for lamp in lamps:
        for prefix in lamp_prefixes:
            if lamp.startswith(prefix):
                set_lamp(lamp, state)

def set_brightness_prefixes(lamp_prefixes: list[str], state: str):
    for lamp in lamps:
        for prefix in lamp_prefixes:
            if lamp.startswith(prefix):
                set_brightness(lamp, state)

def set_lamp_except_prefixes(lamp_prefixes: list[str], state: str):
    for lamp in lamps:
        for prefix in lamp_prefixes:
            if lamp.startswith(prefix):
                break
        else:
            set_lamp(lamp, state)

last_state = None

if __name__ == "__main__":
    while True:
        sleep(1)

        state = jellyfin.get_state()

        if state is not last_state:

            if state == jellyfin.PLAYING:
                set_lamp_except_prefixes(('olohuone3', 'eteinen2'), "OFF")
                set_brightness_prefixes(('olohuone3', 'eteinen2'), "10")
            else:
                set_lamp_prefixes(('',), "ON")
                set_brightness_prefixes(('',), "255")

            last_state = state

