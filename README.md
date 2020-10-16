[start script]

```
# pip install prometheus_client requests
# curl -O https://raw.githubusercontent.com/tnaganawa/tf-analytics-exporter/master/tf-analytics-exporter.py
# ./tf-analytics-exporter.py
 - run this on tungsten fabric control / analytics / config node
```
 
  
```
# curl 127.0.0.1:11234
 -> see if metrics are given
```
   
    
[other tools]

```
# docker run --net=host -v /root/prometheus.yml:/etc/prometheus/prometheus.yml -v /root/tf-alarm.yml:/etc/prometheus/tf-alarm.yml prom/prometheus
# docker run -d -p 3000:3000 grafana/grafana
```
