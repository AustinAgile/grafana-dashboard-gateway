{{- define "grafana-dashboard-gateway.name" -}}
grafana-dashboard-gateway
{{- end -}}

{{- define "global.annotations.standard" }}
Release.Name: {{ .Release.Name | quote }}
Release.Revision: {{ .Release.Revision | quote }}
Release.Heritage: {{ .Release.Service | quote }}
Chart.Name: {{ .Chart.Name | quote }}
Chart.Version: {{ .Chart.Version | quote }}
{{- end }}
