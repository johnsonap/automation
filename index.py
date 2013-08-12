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

app = Flask(__name__)


@app.route('/flag')
def flag():
    
    flag_page = Soup(urllib2.urlopen('http://www.visitpanamacitybeach.com/controller.cfm?plugin=beachFlags&object=currentFlagApi&action=getAjax&startrow=1&rows=1&paginate=true&orderby=updated+desc').read())
    flag_page = str(flag_page)
    flag_page = flag_page[:flag_page.index('meta')-2]+'}}}'
    flag_data = json.loads(flag_page)
    flag_color = flag_data['data']['data']['result'][0]['code']
    data = db.flag.find_one({'data':'flag'})
    if not data:
        data = {'data':'flag', 'status':flag_color}
    else:
        data['status'] = flag_color
    db.flag.save(data)
    
    return flag_page, 200, {'Content-Type': 'text/plain'}

@app.route('/')
def index():
    now_time = datetime.datetime.now()
    weather_data = db.weather.find_one({'data':'weather'})['json']

    flag = db.flag.find_one({'data':'flag'})['status']
    sunset = weather_data['sun_phase']['sunset']
    sunrise = weather_data['sun_phase']['sunrise']
    night = False
    hvac_data = db.hvac.find_one({'data':'hvac'})['json']
    
    print sunset['hour']
    print now_time.hour
    if int(sunset['hour']) < int(now_time.hour):
        night = True
    if int(sunset['hour']) == int(now_time.hour):
        if int(sunset['minute']) <= int(now_time.minute):
            night = True
    if int(sunrise['hour']) > int(now_time.hour):
        night = True
    if int(sunrise['hour']) == int(now_time.hour):
        if int(sunrise['minute']) >= int(now_time.minute):
            night = True
            
            
    return render_template('index.html',weather=weather_data, night=night, flag=flag, hvac=hvac_data)


@app.route('/weather')
def weather():
    url = "http://api.wunderground.com/api/3bb540c93093fad7/geolookup/conditions/forecast/astronomy/forecast10day/q/32408.json"
    usock = urllib2.urlopen(url)
    weather_data = usock.read()
    datan = json.loads(weather_data)
    usock.close()
    data = db.weather.find_one({'data':'weather'})
    if not data:
        data = {'data':'weather', 'json':datan}
    else:
        data['json'] = datan
    db.weather.save(data)
    return weather_data, 200, {'Content-Type': 'text/plain'}

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
    temp
    hvac_data = db.hvac.find_one({'data':'hvac'})
    hvac_data['json']['current_temp'] = temp
    db.hvac.save(hvac_data)
    return temp, 200, {'Content-Type': 'text/plain'}
    
@app.route('/hvac/setting/<setting_one>/<setting_two>')
def settings(setting_one, setting_two):
    hvac_data = db.hvac.find_one({'data':'hvac'})
    hvac_data['json']['hvac_setting'] = setting_one
    hvac_data['json']['on_off'] = setting_two
    db.hvac.save(hvac_data)
    return "ok", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)