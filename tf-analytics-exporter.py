#!/usr/bin/env python
import sys
import os
import time
import json
import requests
from prometheus_client import start_http_server, Metric, REGISTRY

class JsonCollector(object):
  def __init__(self, endpoint):
    self._endpoint = 'http://' + endpoint + ':8081/analytics/uves/vrouter/*?flat'

  def collect(self):

    ##
    # get metrics for vrouters from analytics:
    ##
    url = self._endpoint

    # Fetch the JSON
    response = json.loads(requests.get(url).content.decode('UTF-8'))
    #print (response)
  
    metric = Metric('vrouter_metrics',
        'metrics for vrouters', 'summary')

    # vRouter UVE
    for entry in response['value']:
      name = entry["name"]
      tmp = entry["value"]["VrouterStatsAgent"]

      drop_stats = tmp["raw_drop_stats"]
      for k in drop_stats:
        metric.add_sample('drop_stats_'+k, value=drop_stats[k], labels={"host_id": name})
 
      flow_rate = tmp["flow_rate"]
      for k in flow_rate:
        metric.add_sample('flow_rate_'+k, value=flow_rate[k], labels={"host_id": name})

      phy_if_stats = tmp["raw_phy_if_stats"]
      phy_if_stats = phy_if_stats.values()[0]
      for k in phy_if_stats:
        metric.add_sample('phy_if_stats_'+k, value=phy_if_stats[k], labels={"host_id": name})

      tmp = entry["value"]["VrouterControlStats"]
      rt_table_size = tmp["raw_rt_table_size"]
      num_of_rt=0
      num_of_routes=0
      for k in rt_table_size:
        num_of_rt+=1
        for kk in rt_table_size[k]:
          num_of_routes+=rt_table_size[k][kk]
      metric.add_sample('num_of_route_tables', value=num_of_rt, labels={"host_id": name})
      metric.add_sample('num_of_routes', value=num_of_routes, labels={"host_id": name})

    yield metric

  

if __name__ == '__main__':
  # Usage: tf-analytics-exporter.py
  http_port=11234
  start_http_server(int(http_port))
  analytics_api_ip=os.popen("netstat -ntlp | grep -w 8081 | awk '{print $4}' | awk -F: '{print $1}'").read().rstrip()
  print(analytics_api_ip)
  REGISTRY.register(JsonCollector(analytics_api_ip))

  while True: time.sleep(1)

