import pandas as pd
import requests 
import os
import math
from xml.etree.ElementTree import fromstring, ElementTree
from datetime import datetime
import json
import statistics 
from collections import Counter 

TrafficEvents = None

chunk_size = 1000
max_distance_from_node = 50 # Meter
number_of_nearest_node = 5 # count

OSM_BASIC_URL = "https://api.openstreetmap.org/api/0.6/"
BASE_PATH = "/home/amin/CETI/RoadConstruction/TrafficEventData/part/"
    
index_folder = 0
index_start_point_file = 0
index_end_point_file = 411

def read_data(path):
    data = None
    print("read csv data is started with file {}".format(path))
    data = pd.read_csv(path)
    print("reading is finished length is {} ".format(len(data)))
    return data


def most_frequent(List): 
    occurence_count = Counter(List) 
    return occurence_count.most_common(1)[0][0]

class OSM(object):
    @staticmethod
    def get_node_details_by_node_id(node_id):
        URL = OSM_BASIC_URL + "node/{}".format(node_id)
        response = requests.get(url = URL)
        result_tree = ElementTree.fromstring(response.content)
        return result_tree, response.content
    
    @staticmethod
    def get_all_ways_contain_node_by_node_id(node_id):
        URL = OSM_BASIC_URL + "node/{}/ways".format(node_id)
        # print(URL)
        response = requests.get(url = URL)
        # result_tree = ElementTree.fromstring(response.content)
        result_tree = ElementTree(fromstring(response.content))

        return result_tree, response.content
    
    @staticmethod
    def get_type_of_way_contain_node_by_node_id(node_id):
        way_type = "None" 
        if node_id == 0:
            return way_type
        try:
            result_tree, content = OSM.get_all_ways_contain_node_by_node_id(node_id)
            root = result_tree.getroot()
            for child in root:
                if child.tag == "way":
                    for child1 in child:
                        if child1.tag == "tag" and child1.attrib["k"] == "highway":
                            way_type = child1.attrib["v"]
                            return way_type
        except:
            print("ERROR: node id {} has error".format(node_id))
            
        return way_type

out_dir = BASE_PATH + "_" + str(index_folder) + "_" 
if not os.path.exists(out_dir):
     os.mkdir(out_dir)

for i in range(index_start_point_file, index_end_point_file):
    type_of_ways_all_points = []
    print("file id is {}".format(i))
    print("start time is {}".format(datetime.now()))
    path = BASE_PATH + "_" + str(index_folder) + "/" + str(i) + "_file_"+ str(i) + ".csv"
    
    traffic_events_data = read_data(path)
    for index, data in traffic_events_data.iterrows():
        start_points_node_id = json.loads(data['nearst_nodes_ids_of_start_point'])
        end_points_node_id = json.loads(data['nearst_nodes_ids_of_end_point'])
        
        start_points_node_id = start_points_node_id[:3]
        end_points_node_id = end_points_node_id[:3]
        
        ways_id = set(start_points_node_id + end_points_node_id)
        type_of_ways = []
        while len(ways_id) > 0:
            node_id = ways_id.pop()
            type_of_way = OSM.get_type_of_way_contain_node_by_node_id(node_id)
            type_of_ways.append(type_of_way)
        type_of_road = most_frequent(type_of_ways)
        if index % 50 == 0:
            print("number: {} is {}".format(index, type_of_road))
            print("Time is {}".format(datetime.now()))
        type_of_ways_all_points.append(type_of_road)
    
    traffic_events_data["type_of_roads"] = type_of_ways_all_points
    
    output_file_url = BASE_PATH + "_" + str(index_folder) + "_/" + str(i) + "_file_"+ str(i) + ".csv"
    traffic_events_data.to_csv (output_file_url, index = False, header=True)
    print(traffic_events_data.columns)
    print("{} done".format(output_file_url))
    print("end time is {}".format(datetime.now()))