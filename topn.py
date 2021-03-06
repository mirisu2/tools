#!/usr/bin/python
"""
Return: top KK outgoing for last NN min and direction
Show: source ip, bytes, packets, flow
Ordered by: bytes
"""
import sys

from elasticsearch import Elasticsearch
from termcolor import colored


try:
    if "out" in sys.argv[3]:
        direction = "source_ipv4_address"
    else:
        direction = "destination_ipv4_address"

    kk = sys.argv[1]
    nn = sys.argv[2]

    body = """
    {
      "size" : 0,
      "_source" : false,
      "stored_fields" : "_none_",
      "track_total_hits": true,
        "query": { 
        "bool": { 
          "filter": [
            { "range": { "@timestamp": {
                "gte": "now-""" + nn + """m",
                "lte": "now"          
            }}},
            { "range": { "netflow.""" + direction + """": {
                "gte": "80.254.16.0",
                "lte": "80.254.31.255"
              }}}
          ]
        }
      },
      "aggs": {
        "group_by" : {
                "terms" : {
                    "field" : "netflow.""" + direction + """",
                    "size" : """ + kk + """,
                    "order" : { "network_bytes" : "desc" }
                },
          "aggs": {
            "network_bytes" : {
              "sum" : { "field" : "network.bytes" }
            },
            "network_packets": {
              "sum" : { "field" : "network.packets" }          
            },
            "flow_count" : { "value_count" : { "field" : "network.bytes" } }

          }
        }
      }
    }
    """

    es = Elasticsearch(['http://192.168.198.101:9200'])
    result = es.search(body=body, index="filebeat-7.7.0-*")
    print "Direction:", colored(direction, "red", attrs=["bold"])
    i = 1
    for bucket in result["aggregations"]["group_by"]["buckets"]:
        print colored(i, "red", attrs=["bold"]), colored("Host:", "green"), bucket["key"], \
            colored("Bytes:", "green"), int(bucket["network_bytes"]["value"]) / 1024 / 1024, "MB", \
            colored("Packets:", "green"), bucket["network_packets"]["value"], \
            colored("Flow:", "green"), bucket["flow_count"]["value"]
        i = i + 1

except IndexError:
    print "\nScript usage: \n$ {} 10 15 out|in\n".format(sys.argv[0])


