[start script]

```
# pip install prometheus_client requests
# python tf-analytics-exporter.py 1234 192.168.122.11
arg:
port-number, TF-analytics-ip
```
 
  
```
# curl 127.0.0.1:1234
 -> see if metrics are given
```
   
    
[other tools]

```
# docker run -d -p 9090:9090 prom/prometheus
# docker run -d -p 3000:3000 grafana/grafana
```
