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
	print(f'Watching kubernetes API')
	v1 = client.CoreV1Api()
	w = watch.Watch()
	stream = w.stream(v1.list_config_map_for_all_namespaces)
	for event in stream:
		metadata = event['object'].metadata
		if metadata.annotations is None:
			continue
		if annotation not in metadata.annotations:
			continue
		if metadata.annotations[annotation] == "dashboard":
			eventType = event['type']
			dataMap=event['object'].data
			if dataMap is None:
				print("---")
				print("Configmap %s/%s dashboard is %s, with no data" % (metadata.namespace, metadata.name, eventType))
				continue
			print("---")
			print("Configmap %s/%s dashboard is %s" % (metadata.namespace, metadata.name, eventType))
			for item in dataMap.keys():
				print("---")
				print("Found a dashboard: %s" % item)
				dashboard = json.loads(dataMap[item])
				update(dashboard)
		if metadata.annotations[annotation] == "datasource":
			datasource(event)


def datasource(event):
	metadata = event['object'].metadata
	eventType = event['type']
	dataMap=event['object'].data
	if dataMap is None:
		print("---")
		print("Configmap %s/%s datasource is %s, with no data" % (metadata.namespace, metadata.name, eventType))
		return
	print("---")
	print("Configmap %s/%s datasource is %s" % (metadata.namespace, metadata.name, eventType))
	for item in dataMap.keys():
		print("---")
		print("Found a datasource: %s" % item)
		ds = json.loads(dataMap[item])
		print("Posting json for datasource: %s ..." % ds["name"])
		r = requests.Session()
		retries = Retry(total = 5,
			connect = 5,
			backoff_factor = 0.2,
			status_forcelist = [ 500, 502, 503, 504 ])
		r.mount('http://', HTTPAdapter(max_retries=retries))
		r.mount('https://', HTTPAdapter(max_retries=retries))
		res = r.post(api+"/datasources", json=ds, timeout=10)
		print("API result: %s" % res.status_code)

def update(dashboard):
	r = requests.Session()
	retries = Retry(total = 5,
		connect = 5,
		backoff_factor = 0.2,
		status_forcelist = [ 500, 502, 503, 504 ])
	r.mount('http://', HTTPAdapter(max_retries=retries))
	r.mount('https://', HTTPAdapter(max_retries=retries))

	if "dashboard" not in dashboard:
		dashboard = {"dashboard": dashboard, "overwrite": True}

#	newTitle = dashboard["dashboard"]["title"] + " (v" + str(dashboard["dashboard"]["version"]) + ")"
#	dashboard["dashboard"]["title"] = newTitle
#	print("Changing title to %s" % newTitle)

	dashboardTitle = dashboard["dashboard"]["title"]
	print("Posting json for dashboard title: %s ..." % dashboardTitle)

	res = r.post(api+"/dashboards/db", json=dashboard, timeout=10)
	print("API result: %s" % res.status_code)

#app = web.Application()
#app.router.add_get('/', handle)
#app.router.add_get('/{name}', handle)

with open('/etc/secret/grafana-dashboard-gateway/admin-user') as f:
	user = f.read()
f.closed
print ("user: %s" % user)

with open('/etc/secret/grafana-dashboard-gateway/admin-password') as f:
	pw = f.read()
f.closed

with open('/etc/config/grafana-dashboard-gateway/grafana-service-name') as f:
	grafanaServiceName = f.read()
f.closed
print ("grafana service name: %s" % grafanaServiceName)

with open('/etc/config/grafana-dashboard-gateway/namespace') as f:
	namespace = f.read()
f.closed
print ("namespace: %s" % namespace)

api = "http://"+user+":"+pw+"@" + grafanaServiceName + "." + namespace + ".svc.cluster.local:3000/api"
print ("grafana api root: %s" % api)

config.load_incluster_config()
print("Config for cluster api loaded...")
watchForChanges()

print('calling web')
#web.run_app(app, port=5858)
