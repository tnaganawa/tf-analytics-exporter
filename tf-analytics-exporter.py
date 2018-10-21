import sys
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

    for entry in response['value']:
      name = entry["name"]
      tmp = entry["value"]["VrouterStatsAgent"]

      drop_stats = tmp["drop_stats"]
      for k in drop_stats:
        metric.add_sample('drop_stats_'+k, value=drop_stats[k], labels={"host_id": name})
 
      flow_rate = tmp["flow_rate"]
      for k in flow_rate:
        metric.add_sample('flow_rate_'+k, value=flow_rate[k], labels={"host_id": name})

      phy_if_stats = tmp["phy_if_stats"]
      phy_if_stats = phy_if_stats.values()[0]
      for k in phy_if_stats:
        metric.add_sample('phy_if_stats_'+k, value=phy_if_stats[k], labels={"host_id": name})

    yield metric

  

if __name__ == '__main__':
  # Usage: tf-analytics-exporter.py port endpoint
  start_http_server(int(sys.argv[1]))
  REGISTRY.register(JsonCollector(sys.argv[2]))

  while True: time.sleep(1)

