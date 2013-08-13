import os, urllib2, datetime, urlparse, re, pusher
import simplejson as json
from bs4 import BeautifulSoup as Soup
from pymongo import Connection
from flask import Flask
from flask import render_template

MONGO_URL = os.environ.get('MONGOHQ_URL')

# check to see if the MONGO_URL exists, otherwise just connect locally
if MONGO_URL:
    connection = Connection(MONGO_URL)
    db = connection[urlparse.urlparse(MONGO_URL).path[1:]]
else:
    connection = Connection('localhost', 27017)
    db = connection['home_automation']

p = pusher.Pusher(app_id='51528', key='bbfd2fdfc81124a36b18', secret='c192b321e8df94b5b127')

app = Flask(__name__,template_folder='static/templates')


@app.route('/')
def index():

    weather_data = db.weather.find_one({'data':'weather'})['json']
    flag = db.flag.find_one({'data':'flag'})['status']
    hvac_data = db.hvac.find_one({'data':'hvac'})['json']
    return render_template('index.html',weather=weather_data, flag=flag, hvac=hvac_data)

@app.route('/hvac')
def hvac():
    data = db.hvac.find_one({'data':'hvac'})
    if not data:
        data = {'data':'hvac', 'json':"json"}
    else:
        data['json'] = "json"
    db.hvac.save(data)
    return "ok", 200, {'Content-Type': 'text/plain'}

@app.route('/hvac/temp/<temp>')
def settemp(temp):
    hvac_data = db.hvac.find_one({'data':'hvac'})
    hvac_data['json']['current_temp'] = temp
    db.hvac.save(hvac_data)
    p['hvac'].trigger('update_temp', {'temp': temp})
    return temp, 200, {'Content-Type': 'text/plain'}
    
@app.route('/hvac/setting/<setting_one>/<setting_two>')
def settings(setting_one, setting_two):
    hvac_data = db.hvac.find_one({'data':'hvac'})
    hvac_data['json']['hvac_setting'] = setting_one
    hvac_data['json']['on_off'] = setting_two
    p['hvac'].trigger('update_settings', {'hvac_setting': setting_one, 'on_off': setting_two})
    db.hvac.save(hvac_data)
    return "ok", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)