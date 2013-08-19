import os, urllib2, datetime, urlparse, re, pusher
import simplejson as json
from bs4 import BeautifulSoup as Soup
from pymongo import Connection
from flask import Flask
from flask import render_template

def include(filename):
    if os.path.exists(filename): 
        execfile(filename)

MONGO_URL = os.environ.get('MONGOHQ_URL')
PUSHER_URL = os.environ.get('PUSHER_URL')
include('config.py')

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
    weather_data = db.settings.find_one({'data':'weather'})['json']
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
    p['hvac'].trigger('update_settings', {'hvac_setting': setting_one, 'on_off': setting_two})
#     db.settings.save(hvac_data)
    return "ok", 200, {'Content-Type': 'text/plain'}
    
@app.route('/lights/<name>/<setting>')
def lights(name, setting):
    hvac_data = db.settings.find_one({'data':'lights'})
    return "ok", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)