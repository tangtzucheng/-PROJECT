import requests
import codecs
import csv
import sys
import json
import urllib
import pymongo
from time import sleep

DB_ADDR='127.0.0.1:27017'
APPID='yFXLV4vVugXSHv0dHDQb'
APPCODE='-yqTDV_rzg0jcv4S-nv-Kg'


def getList():
	r=requests.get("https://data.chiayi.gov.tw/opendata/api/getResource?oid=b1bdb8f9-d0ae-4de6-8ce4-4addec23e44b&rid=049a78fe-3328-472a-bcd5-b24a997050ce")
	if r.status_code != 200:
		exit(1)
	camList=r.text.replace(',"\n',',').replace('"','')
	camList=camList.replace('嘉義市政府警察局治安要點錄影監視系統一覽表,\r\n','')
	camList=camList.replace('編號,地點','id,location,lat,lng')
	with codecs.open('loc.csv','w','utf-8') as f:
		f.write(camList)

def process():
	camList=[]
	with codecs.open('loc.csv','r','utf-8') as f:
		reader=csv.DictReader(f)
		for cam in reader:
			camList.append(cam)
	withdir=[]
	multi=[]
	intr=[]
	other=[]
	for cam in camList:
		if '往' in cam['location'] or '向' in cam['location']:
			if '東' in cam['location'] or '西' in cam['location'] or '南' in cam['location'] or '北' in cam['location']:
				withdir.append(cam)
				continue
		intrc=0
		intrc+=cam['location'].count('、')
		intrc+=cam['location'].count('與')
		if intrc>=2:
			multi.append(cam)
		elif intrc==1:
			intr.append(cam)
		else:
			other.append(cam)
	counter=1
	for i in intr:
		loc=i['location'].replace('巷口','巷').replace('路口','路').replace('街口','街')
		loc=loc.replace('、','@').replace('與','@')
		param={'city':'嘉義市','street':loc,'app_id':APPID,'app_code':APPCODE,'gen':'9'}
		url='https://geocoder.api.here.com/6.2/geocode.json?'+urllib.parse.urlencode(param)
		r=requests.get(url)
		print('intr'+str(counter))
		counter+=1
		if r.status_code!=200:
			continue
		j=json.loads(r.text)
		if len(j['Response']['View']) == 0:
			continue
		i['longitude']=j['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude']
		i['latitude']=j['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude']
		col.insert_one(i)
		sleep(0.1)
	counter=1
	for i in other:
		param={'app_id':APPID,'app_code':APPCODE,'searchtext':i['location']+', 嘉義市'}
		url='https://geocoder.api.here.com/6.2/geocode.json?'+urllib.parse.urlencode(param)
		r=requests.get(url)
		print('intr'+str(counter))
		counter+=1
		if r.status_code !=200:
			continue
		j=json.loads(r.text)
		if len(j['Response']['View']) == 0:
			continue
		i['longitude']=j['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude']
		i['latitude']=j['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude']
		col.insert_one(i)
		sleep(0.1)
		
	with codecs.open('multi.txt','w','utf-8') as f:
		for i in multi:
			f.write(str(i))
			f.write('\n')
	with codecs.open('dir.txt','w','utf-8') as f:
		for i in withdir:
			f.write(str(i))
			f.write('\n')
	with codecs.open('intr.txt','w','utf-8') as f:
		for i in intr:
			f.write(str(i))
			f.write('\n')
	with codecs.open('other.txt','w','utf-8') as f:
		for i in other:
			f.write(str(i))
			f.write('\n')
	
	autoList=[]
	none=[]
	autoList.extend(intr)
	autoList.extend(other)
	for i in autoList:
		if i['longitude'] == None or i['latitude'] == None:
			none.append(i)
	with codecs.open('none.txt','w','utf-8') as f:
		for i in none:
			f.write(str(i))
			f.write('\n')

def updatedb():
	id=input('id=')
	loc=input('location=')
	lat=input('latitude=')
	lon=input('longitude=')
	dic={'id':id,'location':loc,'latitude':lat,'longitude':lon}
	col.update_one({'id':id,'location':loc},{'$set':dic},upsert=True)
	
def _init_():
	args=str(sys.argv)
	do=False
	if 'clear' in args:
		col.delete_many({})
		do=True
	if 'getList' in args:
		getList()
		do=True
	if 'process' in args:
		process()
		do=True
	if 'update' in args:
		updatedb()
		do=True
	if 'test' in args:
		do=True
	if not do:
		print('do nothing')


client=pymongo.MongoClient(DB_ADDR)
db=client["map"]
col=db["cams"]
_init_()