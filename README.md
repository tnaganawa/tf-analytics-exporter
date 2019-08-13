[start script]

```
# pip install prometheus_client requests
# curl -O https://raw.githubusercontent.com/vcheny/contrail-introspect-cli/master/ist.py
# cp -ip ist.py /usr/bin/
# curl -O https://raw.githubusercontent.com/tnaganawa/tf-analytics-exporter/master/tf-analytics-exporter.py
# ./tf-analytics-exporter.py
 - run this on tungsten fabric controller / analytics node
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
