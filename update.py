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

settings_data = db.settings.find_one({'data':'settings'})['json']

forecast_url = "https://api.forecast.io/forecast/b4e07ec19b8a1b7a98536d29f0f42dd3/30.1466,-85.7596"
usock = urllib2.urlopen(forecast_url)
weather_data = usock.read()
weather_data = json.loads(weather_data)
usock.close()

forecast_data = {}
if 'alerts' in weather_data.keys():
    forecast_data['alerts'] = weather_data['alerts']
forecast_data['currently'] = weather_data['currently']
forecast_data['currently']['temperature'] = int(round(forecast_data['currently']['temperature'],0))
forecast_data['currently']['location'] = settings_data['location']
forecast_data['summaries'] = {}
forecast_data['summaries']['hour'] = weather_data['minutely']['summary']
forecast_data['summaries']['hours'] = weather_data['hourly']['summary']
forecast_data['forecast'] = weather_data['daily']
forecast_data['currently']['windSpeed'] = round(forecast_data['currently']['windSpeed'] * .8689,1)
forecast_data['currently']['humidity'] = int(round(forecast_data['currently']['humidity'] *100, 0))
windBearing = forecast_data['currently']['windBearing']
wind_string = ''
if windBearing > 337.5 or windBearing < 22.5:
    wind_string = 'N'
if windBearing > 67.5 and windBearing < 112.5:
    wind_string = 'E'
if windBearing > 157.5 and windBearing < 202.5:
    wind_string = 'S'
if windBearing > 247.5 and windBearing < 292.5:
    wind_string = 'W'
if windBearing > 22.5 and windBearing < 67.5:
    wind_string = 'NE'
if windBearing > 112.5 and windBearing < 157.5:
    wind_string = 'SE'
if windBearing > 292.5 and windBearing < 337.5:
    wind_string = 'NW'
if windBearing > 202.5 and windBearing < 247.5:
    wind_string = 'SW'
forecast_data['currently']['wind_string'] = wind_string
for day in forecast_data['forecast']['data']:
    day['temperatureMin'] = int(round(day['temperatureMin'],0))
    day['temperatureMax'] = int(round(day['temperatureMax'],0))
    day['time'] = datetime.date.fromtimestamp(day['time']).strftime('%a')
    
    del day['ozone']
    del day['temperatureMinTime']
    del day['temperatureMaxTime']
    del day['pressure']
    del day['cloudCover']
    del day['humidity']
    del day['dewPoint']
    del day['sunriseTime']
    del day['sunsetTime']
    del day['apparentTemperatureMin']
    del day['apparentTemperatureMax']
    del day['apparentTemperatureMinTime']
    del day['apparentTemperatureMaxTime']
    del day['precipIntensity']
    del day['precipProbability']
    del day['precipType']
    day['windSpeed'] = round(day['windSpeed'] * .8689,1)

forecast_data['forecast'] = forecast_data['forecast']['data']
flag_page = Soup(urllib2.urlopen('http://www.visitpanamacitybeach.com/controller.cfm?plugin=beachFlags&object=currentFlagApi&action=getAjax&startrow=1&rows=1&paginate=true&orderby=updated+desc').read())
flag_page = str(flag_page)
flag_page = flag_page[:flag_page.index('meta')-2]+'}}}'
flag_data = json.loads(flag_page)
flag_color = flag_data['data']['data']['result'][0]['code']
forecast_data['currently']['flag_color'] = flag_color

p['weather'].trigger('weather', {'weather': forecast_data })



forecast_db = db.settings.find_one({'data':'forecast_api'})
forecast_db['json'] = forecast_data
db.settings.save(forecast_db)




