#!/usr/bin/env python
import sys
import os
import time
import json
import requests
from prometheus_client import start_http_server, Metric, REGISTRY

class JsonCollector(object):
  def __init__(self, analytics_api_ip, control_api_ip, config_api_ip):
    self._endpoint = 'http://' + analytics_api_ip + ':8081/analytics/uves/'
    self.vrouter_endpoint = self._endpoint + 'vrouter/*?flat'
    self.control_endpoint = self._endpoint + 'control-node/*?flat'
    self.config_database_endpoint = self._endpoint + 'config-database-node/*?flat'
    self.database_endpoint = self._endpoint + 'database-node/*?flat'
    self.analytics_endpoint = self._endpoint + 'analytics-node/*?flat'
    self.config_endpoint = self._endpoint + 'config-node/*?flat'
    self.control_api_ip = control_api_ip
    self.config_api_ip = config_api_ip

  def collect(self):

    metric = Metric('tungstenfabric_metrics',
        'metrics for tungsten fabric', 'summary')

    ##
    # config-database node / database node
    ##
    url = self.config_database_endpoint
    response = json.loads(requests.get(url).content.decode('UTF-8'))
    config_database_list=response['value']

    url = self.database_endpoint
    response = json.loads(requests.get(url).content.decode('UTF-8'))
    analytics_database_list=response['value']
  
    url = self.config_endpoint
    response = json.loads(requests.get(url).content.decode('UTF-8'))
    config_node_list=response['value']

    url = self.analytics_endpoint
    response = json.loads(requests.get(url).content.decode('UTF-8'))
    analytics_list=response['value']

    ##
    # get metrics for vrouters from analytics:
    ##
    url = self.vrouter_endpoint
    response = json.loads(requests.get(url).content.decode('UTF-8'))
    vrouter_node_list = response['value']


    ##
    # control-node
    ##
    url = self.control_endpoint
    response = json.loads(requests.get(url).content.decode('UTF-8'))
    control_node_list=response['value']

    for entry in config_database_list + analytics_database_list:
      name = entry["name"]
      value = entry["value"]
      node_type=value.get("NodeStatus").get("system_cpu_usage").get("node_type")

      ##
      # system_defined_pending_cassandra_compaction_tasks
      ##
      pending_compaction_tasks=value.get("CassandraStatusData").get("cassandra_compaction_task").get("pending_compaction_tasks")
      metric.add_sample('pending_compaction_tasks', value=pending_compaction_tasks, labels={"host_id": name, "node_type": node_type})

  
    for entry in control_node_list + config_node_list + vrouter_node_list + config_database_list + analytics_list + analytics_database_list:
      name = entry["name"]
      value = entry["value"]
      node_type=value.get("NodeStatus").get("system_cpu_usage").get("node_type")

      ##
      # system_defined_conf_in_correct
      ##
      contrail_config=value.get("ContrailConfig")
      if contrail_config == None:
        tmp = 1
      else:
        tmp = 0
      metric.add_sample('system_defined_conf_incorrect', value=tmp, labels={"host_id": name, "node_type": node_type})

      ##
      # system_defined_node_status
      ##
      node_status=value.get("NodeStatus")
      if node_status == None:
        tmp = 1
      else:
        tmp = 0
      metric.add_sample('system_defined_node_status', value=tmp, labels={"host_id": name, "node_type": node_type})

      ##
      # system_defined_partial_sysinfo
      ##
      node_status_build_info=value.get("NodeStatus").get("build_info")
      if node_status_build_info == None:
        tmp = 1
      else:
        tmp = 0
      metric.add_sample('system_defined_parital_sysinfo', value=tmp, labels={"host_id": name, "node_type": node_type})

      ##
      # system_defined_package_version_mismatch
      ##
      running_package_version=value.get("NodeStatus").get("running_package_version")
      installed_package_version=value.get("NodeStatus").get("installed_package_version")
      if running_package_version == installed_package_version:
        tmp = 0
      else:
        tmp = 1
      metric.add_sample('system_defined_package_version_mismatch', value=tmp, labels={"host_id": name, "node_type": node_type})

      ##
      # system_defined_core_files
      ##
      all_core_file_list=value.get("NodeStatus").get("all_core_file_list")
      if all_core_file_list == None:
        tmp = 0
      else:
        if len (all_core_file_list) > 0:
          tmp = 1
        else:
          tmp = 0
      metric.add_sample('system_defined_core_files', value=tmp, labels={"host_id": name, "node_type": node_type})

      ##
      # system_defined_process_connectivity
      ##
      node_status_process_status=value.get("NodeStatus").get("process_status")
      #print (value)
      if node_status_process_status == None:
        tmp = 1
      else:
        tmp = 0
      metric.add_sample('system_defined_process_connectivity', value=tmp, labels={"host_id": name, "node_type": node_type})

      process_status_list = node_status_process_status
      #print (process_status_list)
      for i in range(len(process_status_list)):
        process_status = process_status_list[i].get("state")
        #print (process_status_list[i])
        if process_status == 'Functional':
          tmp = 0
        else:
          tmp = 1
        metric.add_sample('process_status', value=tmp, labels={"host_id": name, "module_id":  process_status_list[i].get("module_id").replace("-","_"), "node_type": node_type})

      ##
      # system_defined_process_status
      ##
      node_status_process_info=value.get("NodeStatus").get("process_info")
      if node_status_process_info == None:
        tmp = 1
      else:
        tmp = 0
      metric.add_sample('system_defined_process_status', value=tmp, labels={"host_id": name, "node_type": node_type})

      process_status_list = node_status_process_info
      for i in range(len(process_status_list)):
        process_info = process_status_list[i].get("process_state")
        #print (process_status_list[i])
        if process_info == 'PROCESS_STATE_RUNNING':
          tmp = 0
        else:
          tmp = 1
        metric.add_sample('process_info', value=tmp, labels={"host_id": name, "process_name": process_status_list[i].get("process_name").replace("-","_"), "node_type": node_type})

      ##
      # system_defined_disk_usage_high / critical
      ##
      disk_usage_info_dict=value.get("NodeStatus").get("disk_usage_info")
      for mountpoint in disk_usage_info_dict:
        disk_usage = disk_usage_info_dict[mountpoint].get("percentage_partition_space_used")
        metric.add_sample('disk_usage', value=int(disk_usage), labels={"host_id": name, "node_type": node_type, "mountpoint": mountpoint.replace("-","_").replace("/", "_")})



    for entry in control_node_list:
      name = entry["name"]
      value = entry["value"]

      ##
      # system_defined_address_mismatch_control
      ##
      ##print dict(json.loads(value.get("ContrailConfig").get("elements").get("bgp_router_parameters"))).get("address")
      bgp_router_param_address=dict(json.loads(value.get("ContrailConfig").get("elements").get("bgp_router_parameters"))).get("address")
      bgp_router_ip_list=value.get("BgpRouterState").get("bgp_router_ip_list")
      if bgp_router_param_address in bgp_router_ip_list:
        tmp = 0
      else:
        tmp = 1
      metric.add_sample('system_defined_address_mismatch_control', value=tmp, labels={"host_id": name})

      ##
      # system_defined_bgp_connectivity
      ##
      num_up_bgp_peer=value.get("BgpRouterState").get("num_up_bgp_peer")
      num_bgp_peer=value.get("BgpRouterState").get("num_bgp_peer")
      metric.add_sample('num_up_bgp_peer', value=num_up_bgp_peer, labels={"host_id": name})
      metric.add_sample('num_bgp_peer', value=num_bgp_peer, labels={"host_id": name})

      ##
      # system_defined_xmpp_connectivity
      ##
      num_up_xmpp_peer=value.get("BgpRouterState").get("num_up_xmpp_peer")
      num_xmpp_peer=value.get("BgpRouterState").get("num_xmpp_peer")
      metric.add_sample('num_up_xmpp_peer', value=num_up_xmpp_peer, labels={"host_id": name})
      metric.add_sample('num_xmpp_peer', value=num_xmpp_peer, labels={"host_id": name})

    ###
    # system_defined_prouter_connectivity: not added
    ###
    ###
    # system_defined_prouter_tsn_connectivity: not added
    ###
    ###
    # system_defined_storage_cluster_state: not added
    ###
    ###
    # system_defined_xmpp_close_reason: not added
    ###


    # vRouter UVE
    for entry in vrouter_node_list:
      name = entry["name"]
      value = entry["value"]


      ##
      # system_defined_address_mismatch_compute
      ##
      try:
        virtual_router_ip_address=value.get("ContrailConfig").get("elements").get("virtual_router_ip_address").replace('"', '')
        control_ip=value.get("VrouterAgent").get("control_ip")
        if virtual_router_ip_address == control_ip:
          tmp = 0
        else:
          tmp = 1
        metric.add_sample('system_defined_address_mismatch_compute', value=tmp, labels={"host_id": name})
      except:
        pass

      ##
      # system_defined_vrouter_limit_exceeded
      ##
      try:
        res_limit=value.get("VrouterAgent").get("res_limit")
        if res_limit == True:
          tmp = 1
        else:
          tmp = 0
        metric.add_sample('system_defined_vrouter_limit_exceeded', value=tmp, labels={"host_id": name})
      except:
        pass

      ##
      # system_defined_vrouter_table_limit_exceeded
      ##
      try:
        res_table_limit=value.get("VrouterAgent").get("res_table_limit")
        if res_table_limit == True:
          tmp = 1
        else:
          tmp = 0
        metric.add_sample('system_defined_vrouter_table_limit_exceeded', value=tmp, labels={"host_id": name})
      except:
        pass

      ##
      # system_defined_vrouter_interface
      ##
      try:
        down_interface_count=value.get("VrouterAgent").get("down_interface_count")
        metric.add_sample('down_interface_count', value=int (down_interface_count), labels={"host_id": name})
      except:
        pass

      ##
      # vRouter perfomance metric
      ##
      try:
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
      except:
        pass

      try:
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
      except:
        pass

    ## control introspect
    #num_of_vns=os.popen ("ist.py ctr route summary -f text | grep -w name | wc -l").read()
    #metric.add_sample('num_of_route_tables', value=num_of_vns, labels={"host_id": self.control_api_ip})
    #num_of_routes=os.popen ("ist.py ctr route summary -f text | grep -w prefixes | awk -F: '{sum+=$2}; END{print sum}'").read()
    #metric.add_sample('num_of_routes', value=num_of_routes, labels={"host_id": self.control_api_ip})
    #num_of_routing_instances=os.popen ("ist.py ctr ri -f text | grep '^  name' | wc -l").read()
    #metric.add_sample('num_of_routing_instances', value=num_of_routing_instances, labels={"host_id": self.control_api_ip})
    #num_of_bgp_blocks=os.popen ("ist.py ctr bgp_stats | grep -w blocked_count | awk -F: '{sum+=$2}; END{print sum}'").read()
    #metric.add_sample('num_of_bgp_blocks', value=num_of_bgp_blocks, labels={"host_id": self.control_api_ip})
    #num_of_bgp_calls=os.popen ("ist.py ctr bgp_stats | grep -w calls | awk -F: '{sum+=$2}; END{print sum}'").read()
    #metric.add_sample('num_of_bgp_calls', value=num_of_bgp_calls, labels={"host_id": self.control_api_ip})
    #num_of_xmpp_blocks=os.popen ("ist.py ctr xmpp stats -f text | grep -w blocked_count | awk -F: '{sum+=$2}; END{print sum}'").read()
    #metric.add_sample('num_of_xmpp_blocks', value=num_of_xmpp_blocks, labels={"host_id": self.control_api_ip})
    #num_of_xmpp_calls=os.popen ("ist.py ctr xmpp stats -f text | grep -w calls | awk -F: '{sum+=$2}; END{print sum}'").read()
    #metric.add_sample('num_of_xmpp_calls', value=num_of_xmpp_calls, labels={"host_id": self.control_api_ip})

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

