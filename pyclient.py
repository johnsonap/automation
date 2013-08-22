import sys, os, serial, time, pusherclient
import simplejson as json

global pusher
arduino = serial.Serial('/dev/tty.usbmodem411')

def lights_callback(data):

    json_data = json.loads(data)
    status = '0'
    if json_data['status'] == 'on':
        status = '1'
    arduino.write('lght' + json_data['light_id'] + status)
    
def connect_handler(data):
    channel = pusher.subscribe("lights")
    channel.bind('update_lights', lights_callback)
    
if __name__ == '__main__':
    pusher = pusherclient.Pusher('bbfd2fdfc81124a36b18')
    pusher.connection.bind('pusher:connection_established', connect_handler)
    while True:
        time.sleep(1)