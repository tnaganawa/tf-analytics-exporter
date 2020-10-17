[start script]

```
# pip install prometheus_client requests
# curl -O https://raw.githubusercontent.com/tnaganawa/tf-analytics-exporter/master/tf-analytics-exporter.py
# ./tf-analytics-exporter.py
 - run this on tungsten fabric control / analytics / config node
or
# docker run -it --net=host --name=tf-analytics-exporter tnaganawa/tf-analytics-exporter
```
 
  
```
# curl 127.0.0.1:11234
 -> see if metrics are given
```
   
    
[other tools]

```
curl -O https://raw.githubusercontent.com/tnaganawa/tf-analytics-exporter/master/prometheus.yml
curl -O https://raw.githubusercontent.com/tnaganawa/tf-analytics-exporter/master/tf-alarm.yml
docker run -d --net=host -v /root/prometheus.yml:/etc/prometheus/prometheus.yml -v /root/tf-alarm.yml:/etc/prometheus/tf-alarm.yml prom/prometheus

curl -O https://raw.githubusercontent.com/tnaganawa/tf-analytics-exporter/master/alertmanager.yml
docker run -d --net=host -v /root/alertmanager.yml:/etc/alertmanager/alertmanager.yml prom/alertmanager


# curl localhost:9090/api/v1/alerts | python -m json.tool
{
    "data": {
        "alerts": [
            {
                "activeAt": "2020-10-16T12:00:28.592862579Z",
                "annotations": {
                    "summary": "Process(es) reporting as non-functional."
                },
                "labels": {
                    "alertname": "system_defined_process_connectivity_2",
                    "host_id": "ip-172-31-10-172.local",
                    "instance": "localhost:11234",
                    "job": "prometheus",
                    "module_id": "contrail_config_database_nodemgr",
                    "node_type": "config-database-node",
                    "severity": "page"
                },
                "state": "firing",
                "value": "1e+00"
            },
            {
...


# docker run -d -p 3000:3000 grafana/grafana
```

[build]

```
cd tf-analytics-exporter
docker build -t tnaganawa/tf-analytics-exporter .
docker login
docker push tnaganawa/tf-analytics-exporter
```
