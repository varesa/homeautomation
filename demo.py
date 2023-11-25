import paho.mqtt.client as mqtt
from time import sleep
import json
import random

DEVICES_TOPIC = 'zigbee2mqtt/bridge/devices'

lamps = []
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
                lamps.append(device['friendly_name'])
            elif definition and 'E2002' in definition.get('model', ''):
                client.subscribe('zigbee2mqtt/' + device['friendly_name'])
        print(lamps)
    else:
        msg = json.loads(message.payload)
        print(msg)
        global action
        action = msg.get('action', '')
        print(action)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost')
client.subscribe(DEVICES_TOPIC)
client.loop_start()

speed = 0.6

while True:
    if action == 'on':
        print('on')
        for lamp in lamps:
            client.publish('zigbee2mqtt/' + lamp + '/set', '{"state": "ON"}')
            sleep(speed)
    if action == 'off':
        print('off')
        for lamp in lamps:
            client.publish('zigbee2mqtt/' + lamp + '/set', '{"state": "OFF"}')
            sleep(speed)
    if action == 'arrow_right_click':
        print('random')
        for lamp in lamps:
            client.publish('zigbee2mqtt/' + lamp + '/set', '{"state": "OFF"}')
        selected = random.choice(lamps)
        client.publish('zigbee2mqtt/' + selected + '/set', '{"state": "ON"}')
    if action == 'arrow_left_click':
        random.shuffle(lamps)
        
    action = ''
    sleep(0.1)
