import sys, os, serial, time, pusherclient
import simplejson as json

global pusher
arduino = serial.Serial('/dev/tty.usbmodem411')

def lights_callback(data):

    lights_data = json.loads(data)
    status = '0'
    if lights_data['status'] == 'on':
        status = '1'
    arduino.write('lght' + lights_data['light_id'] + status)
    
def hvacsettings_callback(data):
    # TODO - update hvac settings
    
def hvactemp_callback(data):
    temp_data = json.loads(data)
    arduino.write('stmp' + json_data['temp'])
    
def connect_handler(data):
    lights_channel = pusher.subscribe("lights") 
    hvac_channel = pusher.subscribe("lights")
    lights_channel.bind('update_lights', lights_callback)
    hvac_channel.bind('update_settings', hvacsettings_callback)
    hvac_channel.bind('update_temp', hvacsettings_callback)
    
if __name__ == '__main__':
    pusher = pusherclient.Pusher('bbfd2fdfc81124a36b18')
    pusher.connection.bind('pusher:connection_established', connect_handler)
    while True:
        time.sleep(1)