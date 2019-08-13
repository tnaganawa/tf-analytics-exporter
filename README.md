[start script]

```
# pip install prometheus_client requests
# ./tf-analytics-exporter.py
```
 
  
```
# curl 127.0.0.1:11234
 -> see if metrics are given
```
   
    
[other tools]

```
# docker run -d -p 9090:9090 prom/prometheus
# docker run -d -p 3000:3000 grafana/grafana
```
