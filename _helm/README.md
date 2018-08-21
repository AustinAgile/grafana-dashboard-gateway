# Grafana Dashboard Gateway

This creates a pod that watches the Kubernetes API for the presence of ConfigMaps with an annotation indicating a Grafana dashboard.
The idea is to develop dashboards in some non-production Grafana instance,
export the JSON into a ConfigMap.
When this ConfigMap is created in some Kubernetes cluster with this pod,
this pod will see it and create/update the dashboard in a target Grafana instance
(identified by a Service name and a Namespace).

## Quick Start ##
The following illustrates a ConfigMap that contains several dashboards.
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-dashboard
  annotations:
    grafana-dashboard-gateway/source: "dashboard"
data:
  {{ (.Files.Glob "dashboards/dashboard1.json").AsConfig }}
  {{ (.Files.Glob "dashboards/dashboard2.json").AsConfig }}
```

The root of the file path referenced in the data property is the root of the Helm chart.

## Dashboard JSON
The JSON exported from the UI looks like this:
```
{
    dashboard json
}
```
The pod changes it to this:
```
{
    dashboard: {
        dashboard json
    },
    overwrite: false,
    folderId: 0

}
```
So you'll notes that dashboards exported through the UI retain everything except the folder they are in.
However, if the exported JSON has been manually updated to already conform to the above JSON structure
then the pod will take it as-is.
So you can export from the UI and "fix" the JSON to include the desired folder.

## Datasources
A dashboard can reference a datasource directly, or can reference a datasource defined as a variable in the dashboard.
When a dashboard is exported through the UI, any datasource reference that is NOT a defined variable will be converted int one.
Hence it is necessary to use defined variables as datasources in any dashboard you want get into Grafana via this pod.
Otherwise the created dashboard will be referencing a datasource variable that is not defined.

## Datasource Variable
You define the datasource as a variable as part of your dashboard.
The dependency that exists is that the datasource your variable references must exist in the target Grafana instance.
This is a matter of establishing standards between dashboard developers and Grafana administrators.