#from aiohttp import web
from kubernetes import client, config, watch
import json
import os
import sys
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import pydash

async def handle(request):
	name = request.match_info.get('name', "World!")
	text = "Hi, and Hello, " + name
	print('received request, replying with "{}".'.format(text))
	return web.Response(text=text)

def watchForChanges():
	annotation = "grafana-dashboard-gateway/source"
	print(f'watching')
	v1 = client.CoreV1Api()
	w = watch.Watch()
	stream = w.stream(v1.list_config_map_for_all_namespaces)
	for event in stream:
		metadata = event['object'].metadata
		if metadata.annotations is None:
			continue
		if annotation not in metadata.annotations:
			continue
		if metadata.annotations[annotation] != "dashboard":
			continue

		eventType = event['type']
		dataMap=event['object'].data
		if dataMap is None:
			print("Configmap %s/%s dashboard is %s, with no data" % (metadata.namespace, metadata.name, eventType))
			continue
		print("Configmap %s/%s dashboard is %s" % (metadata.namespace, metadata.name, eventType))
		for item in dataMap.keys():
			print("Dashboard file: %s" % item)
			dashboard = json.loads(dataMap[item])
			dashboardTitle = dashboard["title"]
			print("Title: %s" % dashboardTitle)
#		uid = search(dashboardTitle)

		update(dashboard)
#		print("requesting")
#		request("http://admin:Abc123!!@grafana.monitoring2.kubernetes.local:32123/api/search", "GET", "")
#		request("http://admin:Abc123!!@grafana.monitoring2.svc.cluster.local:3000/api/datasources/name/Monitoring", "POST", "")

def search(dashboardTitle):
	r = requests.Session()
	retries = Retry(total = 5,
			connect = 5,
			backoff_factor = 0.2,
			status_forcelist = [ 500, 502, 503, 504 ])
	r.mount('http://', HTTPAdapter(max_retries=retries))
	r.mount('https://', HTTPAdapter(max_retries=retries))
	res = r.get("http://admin:Abc123!!@grafana.monitoring2.svc.cluster.local:3000/api/api/search", timeout=10)
	dashboards = res.json()
#	print ("search result:")
#	print (dashboards)
	xyz = pydash.collections.find(dashboards, lambda db: db["title"] == dashboardTitle)
#	print ("pydash")
#	print (xyz)
	print ("uid={}".format(xyz["uid"]))
	return xyz["uid"]

def update(dashboard):
	r = requests.Session()
	retries = Retry(total = 5,
			connect = 5,
			backoff_factor = 0.2,
			status_forcelist = [ 500, 502, 503, 504 ])
	r.mount('http://', HTTPAdapter(max_retries=retries))
	r.mount('https://', HTTPAdapter(max_retries=retries))
	print("xxx update")
#	print(dashboard)
	print(json.dumps(dashboard))
	res = r.post("http://admin:Abc123!!@grafana.monitoring2.svc.cluster.local:3000/api/dashboards/db", json={"dashboard": dashboard, "overwrite": True}, timeout=10)
	print(res.status_code)
	result = res.json()
	print ("update result:")
#	print (result)

def request(url, method, payload):
	print("in request method")
	r = requests.Session()
	retries = Retry(total = 5,
			connect = 5,
			backoff_factor = 0.2,
			status_forcelist = [ 500, 502, 503, 504 ])
	r.mount('http://', HTTPAdapter(max_retries=retries))
	r.mount('https://', HTTPAdapter(max_retries=retries))
	if url is None:
		print("No url provided. Doing nothing.")
		# If method is not provided use GET as default
	elif method == "GET" or method is None:
		print("doing a get %s" % url)
		res = r.get("%s" % url, timeout=10)
		print ("%s request sent to %s. Response: %d %s" % (method, url, res.status_code, res.reason))
		print (res.json())
	elif method == "POST":
		res = r.post("%s" % url, json=payload, timeout=10)
		print ("%s request sent to %s. Response: %d %s" % (method, url, res.status_code, res.reason))

#app = web.Application()
#app.router.add_get('/', handle)
#app.router.add_get('/{name}', handle)

config.load_incluster_config()
print("Config for cluster api loaded...")
print('calling watch')
watchForChanges()

print('calling web')
#web.run_app(app, port=5858)
