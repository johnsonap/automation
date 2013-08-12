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


p['flag'].trigger('update_flag', {"flag_color": flag_color})