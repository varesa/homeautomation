import paho.mqtt.client as mqtt
from time import sleep
import json
import random
from traceback import print_exc

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
            client.subscribe('zigbee2mqtt/' + device['friendly_name'])
        print("lamps:", lamps)
    else:
        try:
            device = message.topic.split('/')[1]
            action = json.loads(message.payload).get('action', '')
            if device and action:
                print("received:", device, action)
                events.append((device, action))
        except Exception:
            print_exc()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost')
client.subscribe(DEVICES_TOPIC)
client.loop_start()


def set_lamp(lamp: str, state: str):
    client.publish('zigbee2mqtt/' + lamp + '/set', '{"state": "' + state + '"}')


def set_lamp_prefixes(lamp_prefixes: list[str], state: str):
    for lamp in lamps:
        for prefix in lamp_prefixes:
            if lamp.startswith(prefix):
                set_lamp(lamp, state)


while True:
    sleep(0.1)

    if not events:
        continue

    events_copy = events.copy()
    events.clear()

    for event in events_copy:
        # Keittiö
        if event == ('kytkin_pyöreä1', 'brightness_up_click'):
            set_lamp_prefixes(('keittiö', 'ruokapöytä'), 'ON')
        if event == ('kytkin_pyöreä1', 'brightness_down_click'):
            set_lamp_prefixes(('keittiö', 'ruokapöytä'), 'OFF')

        # Olohuone
        if event == ('kytkin_iso2', 'on'):
            set_lamp_prefixes(('olohuone',), 'ON')
        if event == ('kytkin_iso2', 'off'):
            set_lamp_prefixes(('olohuone',), 'OFF')

        # Eteinen
        if event == ('kytkin_iso1', 'on'):
            set_lamp_prefixes(('eteinen',), 'ON')
        if event == ('kytkin_iso1', 'off'):
            set_lamp_prefixes(('eteinen',), 'OFF')

        # Työhuone
        if event == ('kytkin_pieni1', 'on'):
            set_lamp_prefixes(('työhuone',), 'ON')
        if event == ('kytkin_pieni1', 'off'):
            set_lamp_prefixes(('työhuone',), 'OFF')

        if event[1] in ('brightness_up_hold', 'brightness_move_up'):
            print('all on')
            set_lamp_prefixes(('', ), 'ON')
        if event[1] in ('brightness_down_hold', 'brightness_move_down'):
            set_lamp_prefixes(('', ), 'OFF')
