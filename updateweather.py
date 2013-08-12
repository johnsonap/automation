import os, urllib2, urlparse, pusher
from bs4 import BeautifulSoup as Soup
import simplejson as json
from time import sleep
from pymongo import Connection

MONGO_URL = os.environ.get('MONGOHQ_URL')

# check to see if the MONGO_URL exists, otherwise just connect locally
if MONGO_URL:
    connection = Connection(MONGO_URL)
    db = connection[urlparse.urlparse(MONGO_URL).path[1:]]
else:
    connection = Connection('localhost', 27017)
    db = connection['home_automation']


p = pusher.Pusher(app_id='51528', key='bbfd2fdfc81124a36b18', secret='c192b321e8df94b5b127')


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

p['weather'].trigger('current_conditions', {'current_conditions': datan['current_observation'],'forecast': datan['forecast']['simpleforecast']['forecastday'][0:6]})