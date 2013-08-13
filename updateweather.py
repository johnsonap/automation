import os, urllib2, urlparse, pusher, datetime
from bs4 import BeautifulSoup as Soup
import simplejson as json
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
datan['current_observation']['temp_f_round'] = int(round(datan['current_observation']['temp_f'],0))

now_time = datetime.datetime.now()
night = False
sunset = datan['sun_phase']['sunset']
sunrise = datan['sun_phase']['sunrise']

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
night_string = ''
if night:
    night_string = 'night'
datan['current_observation']['night'] = night
datan['current_observation']['night_string'] = night_string
datan['current_observation']['flag_color'] = flag_color
wind_string = ''
windspeed =  float(datan['current_observation']['wind_mph']) * 0.868976242
if( windspeed <1):
    wind_string = 'Calm'
else:
    wind_string = str(round(windspeed,2)) + ' knots, ' + datan['current_observation']['wind_dir']


datan['current_observation']['wind_string'] = wind_string

data = db.weather.find_one({'data':'weather'})
if not data:
    data = {'data':'weather', 'json':datan}
else:
    data['json'] = datan
db.weather.save(data)

p['weather'].trigger('current_conditions', {'current_observation': datan['current_observation'],'forecast':{'simpleforecast':{'forecastday': datan['forecast']['simpleforecast']['forecastday'][0:7]}}})



