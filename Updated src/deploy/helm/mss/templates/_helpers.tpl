{{- define "mss.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "mss.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "mss.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}