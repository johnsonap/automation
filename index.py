import os, urllib2, datetime, urlparse, re, pusher
import simplejson as json
from bs4 import BeautifulSoup as Soup
from pymongo import Connection
from flask import Flask
from flask import render_template

MONGO_URL = os.environ.get('MONGOHQ_URL')
PUSHER_URL = os.environ.get('PUSHER_URL')

# check to see if the MONGO_URL exists, otherwise just connect locally
if MONGO_URL:
    connection = Connection(MONGO_URL)
    db = connection[urlparse.urlparse(MONGO_URL).path[1:]]
else:
    connection = Connection('localhost', 27017)
    db = connection['home_automation']
if PUSHER_URL:
    p = pusher.pusher_from_url()
else:
    p = pusher.Pusher(app_id= os.environ.get('PUSHER_APP_ID'), key=os.environ.get('PUSHER_KEY'), secret= os.environ.get('PUSHER_SECRET'))

app = Flask(__name__,template_folder='static/templates')

@app.route('/')
def index():
    weather_data = db.settings.find_one({'data':'forecast_api'})['json']
    hvac_data = db.settings.find_one({'data':'hvac'})['json']
    light_data = db.settings.find_one({'data':'lights'})['light_list']
    settings = db.settings.find_one({'data':'settings'})['json']
    return render_template('index.html',weather=weather_data, hvac=hvac_data, lights=light_data, settings=settings)

@app.route('/settings/current_tab/<tab>')
def set_tab(tab):
    setting_data = db.settings.find_one({'data':'settings'})
    setting_data['json']['current_tab'] = tab;
    db.settings.save(setting_data)
    return "ok", 200, {'Content-Type': 'text/plain'}

@app.route('/settings/zip_code/<zip_code>')
def set_zip(zip_code):
    setting_data = db.settings.find_one({'data':'settings'})
    setting_data['json']['zip_code'] = zip_code;
    db.settings.save(setting_data)
    os.system("python update.py")
    return "ok", 200, {'Content-Type': 'text/plain'}

@app.route('/hvac/temp/<temp>/<client_id>')
def settemp(temp, client_id):
    hvac_data = db.settings.find_one({'data':'hvac'})
    hvac_data['json']['current_temp'] = temp
    db.settings.save(hvac_data)
    p['hvac'].trigger('update_temp', {'temp': temp, 'id':client_id})
    return temp, 200, {'Content-Type': 'text/plain'}

@app.route('/hvac/setting/<setting_one>/<setting_two>')
def settings(setting_one, setting_two):
    hvac_data = db.settings.find_one({'data':'hvac'})
    hvac_data['json']['hvac_setting'] = setting_one
    hvac_data['json']['on_off'] = setting_two
    db.settings.save(hvac_data)
    p['hvac'].trigger('update_settings', {'hvac_setting': setting_one, 'on_off': setting_two})
    return "ok", 200, {'Content-Type': 'text/plain'}
    
@app.route('/lights/<name>/<status>')
def lights(name, status):
    light_data = db.settings.find_one({'data':'lights'})
    for light in light_data['light_list']:
        if light['name'] == name:
            light['status'] = status
    db.settings.save(light_data)
    p['lights'].trigger('update_lights', {'name': name, 'status': status})
    return "ok", 200, {'Content-Type': 'text/plain'}

@app.route('/lights/off')
def lights_off():
    light_data = db.settings.find_one({'data':'lights'})
    for light in light_data['light_list']:
        light['status'] = 'off'
    db.settings.save(light_data)
    p['lights'].trigger('all_lights', {'status': 'off'})
    return "ok", 200, {'Content-Type': 'text/plain'}

@app.route('/lights/on')
def lights_on():
    light_data = db.settings.find_one({'data':'lights'})
    for light in light_data['light_list']:
        light['status'] = 'on'
    db.settings.save(light_data)
    p['lights'].trigger('all_lights', {'status': 'on'})
    return "ok", 200, {'Content-Type': 'text/plain'}
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)