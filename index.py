import os, urllib2, datetime, urlparse, re
import simplejson as json
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

app = Flask(__name__)

@app.route('/')
def index():
    now_time = datetime.datetime.now()
    weather_data = db.weather.find_one({'data':'weather'})['json']

    sunset = weather_data['sun_phase']['sunset']
    sunrise = weather_data['sun_phase']['sunrise']
    night = False
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
            
            
    return render_template('index.html',weather=weather_data, night=night)


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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)