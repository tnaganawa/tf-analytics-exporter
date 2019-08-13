#!/usr/bin/env python
import sys
import os
import time
import json
import requests
from prometheus_client import start_http_server, Metric, REGISTRY

class JsonCollector(object):
  def __init__(self, analytics_api_ip, control_api_ip, config_api_ip):
    self._endpoint = 'http://' + analytics_api_ip + ':8081/analytics/uves/vrouter/*?flat'
    self.control_api_ip = control_api_ip
    self.config_api_ip = config_api_ip

  def collect(self):

    ##
    # get metrics for vrouters from analytics:
    ##
    url = self._endpoint

    # Fetch the JSON
    response = json.loads(requests.get(url).content.decode('UTF-8'))
    #print (response)
  
    metric = Metric('tungstenfabric_metrics',
        'metrics for tungsten fabric', 'summary')

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

    # control introspect
    num_of_vns=os.popen ("ist.py ctr route summary -f text | grep -w name | wc -l").read()
    metric.add_sample('num_of_route_tables', value=num_of_vns, labels={"host_id": self.control_api_ip})
    num_of_routes=os.popen ("ist.py ctr route summary -f text | grep -w prefixes | awk -F: '{sum+=$2}; END{print sum}'").read()
    metric.add_sample('num_of_routes', value=num_of_routes, labels={"host_id": self.control_api_ip})
    num_of_routing_instances=os.popen ("ist.py ctr ri -f text | grep '^  name' | wc -l").read()
    metric.add_sample('num_of_routing_instances', value=num_of_routing_instances, labels={"host_id": self.control_api_ip})
    num_of_bgp_blocks=os.popen ("ist.py ctr bgp_stats | grep -w blocked_count | awk -F: '{sum+=$2}; END{print sum}'").read()
    metric.add_sample('num_of_bgp_blocks', value=num_of_bgp_blocks, labels={"host_id": self.control_api_ip})
    num_of_bgp_calls=os.popen ("ist.py ctr bgp_stats | grep -w calls | awk -F: '{sum+=$2}; END{print sum}'").read()
    metric.add_sample('num_of_bgp_calls', value=num_of_bgp_calls, labels={"host_id": self.control_api_ip})
    num_of_xmpp_blocks=os.popen ("ist.py ctr xmpp stats -f text | grep -w blocked_count | awk -F: '{sum+=$2}; END{print sum}'").read()
    metric.add_sample('num_of_xmpp_blocks', value=num_of_xmpp_blocks, labels={"host_id": self.control_api_ip})
    num_of_xmpp_calls=os.popen ("ist.py ctr xmpp stats -f text | grep -w calls | awk -F: '{sum+=$2}; END{print sum}'").read()
    metric.add_sample('num_of_xmpp_calls', value=num_of_xmpp_calls, labels={"host_id": self.control_api_ip})

    # configdb
    config_api_url = 'http://' + self.config_api_ip + ':8082/'

    response = json.loads(requests.get(config_api_url + 'virtual-networks').content.decode('UTF-8'))
    num_of_virtual_networks = len(response['virtual-networks'])
    metric.add_sample('num_of_virtual_networks', value=num_of_virtual_networks, labels={"host_id": self.config_api_ip})

    response = json.loads(requests.get(config_api_url + 'logical-routers').content.decode('UTF-8'))
    num_of_logical_routers = len(response['logical-routers'])
    metric.add_sample('num_of_logical_routers', value=num_of_logical_routers, labels={"host_id": self.config_api_ip})

    response = json.loads(requests.get(config_api_url + 'projects').content.decode('UTF-8'))
    num_of_projects = len(response['projects'])
    metric.add_sample('num_of_projects', value=num_of_projects, labels={"host_id": self.config_api_ip})

    response = json.loads(requests.get(config_api_url + 'virtual-machine-interfaces').content.decode('UTF-8'))
    num_of_virtual_machine_interfaces = len(response['virtual-machine-interfaces'])
    metric.add_sample('num_of_virtual_machine_interfaces', value=num_of_virtual_machine_interfaces, labels={"host_id": self.config_api_ip})

    yield metric

  

if __name__ == '__main__':
  # Usage: tf-analytics-exporter.py
  http_port=11234
  start_http_server(int(http_port))
  analytics_api_ip=os.popen("netstat -ntlp | grep -w 8081 | awk '{print $4}' | awk -F: '{print $1}'").read().rstrip()
  control_api_ip=analytics_api_ip ## temporary
  config_api_ip=analytics_api_ip ## temporary
  #print(analytics_api_ip)
  REGISTRY.register(JsonCollector(analytics_api_ip, control_api_ip, config_api_ip))

  while True: time.sleep(1)

