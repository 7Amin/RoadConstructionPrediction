import pandas as pd
import requests 
import os
import math
from xml.etree import ElementTree
from datetime import datetime

TrafficEvents = None

chunk_size = 10 ** 3
max_distance_from_node = 50 # Meter
number_of_nearest_node = 5 # count

OSRM_BASIC_URL = "https://usaeta.bluebitsoft.com/"
TrafficEvents = {
    "name": "TrafficEvents",
    # "file_name": "TrafficEvents_Aug16_Dec19_Publish_Road_Construction.csv",
    "file_name": "All_Constructions_June2020_Combined_TO_StartEnd_30_100.csv",
    "path": "/home/amin/CETI/RoadConstruction/TrafficEventData/",
    "part_path": "part"
}
    
index_folder = 0
index_start_point_file = 0
index_end_point_file = 411

traffic_filters = {
    "keys": ["Type"],
    "values": ["Construction"],
    }

def read_big_data_by_filter_with_key_values(path, filters):
    data = None
    print("method {} is started ".format("read_big_data_filter_with_key_values"))
    print("read csv data is started with file {}".format(path))
    print("chunk size is {}".format(chunk_size))
    for key, value in zip(filters['keys'], filters['values']):
        print("the key is {} and the value is {}".format(filters['keys'], filters['values']))
    for num, df in enumerate(pd.read_csv(path, chunksize=chunk_size), start=1):
        print("continue reading file page num is {}".format(num))
        for key, value in zip(filters['keys'], filters['values']):
            df = df[df[key] == value]
        data = df.append(data)
    print("method {} finished ".format("read_big_data_filter_with_key_values"))
    return data

class Location(object):
    def __init__(self, osrm_data):
        self.longitude = osrm_data[0]
        self.latitude = osrm_data[1]

class WayPoint(object):
    def __init__(self, json_data):
        self.nodes = json_data["nodes"]
        self.hint = json_data["hint"]
        self.distance = json_data["distance"]
        self.name = json_data["name"]
        self.location = Location(json_data["location"])
    
    def validate_way_point(self):
        if self.distance < max_distance_from_node:
            return True
        return False

class OSRM(object):
    @staticmethod
    def get_all_nearest_nodes_of_location(location, number=1):
        params = {
            "number": number
        }
        URL = OSRM_BASIC_URL + "nearest/v1/driving/{},{}".format(location.longitude, location.latitude)
        response = requests.get(url = URL, params = params)
        return response.json() 


dir = os.path.join(TrafficEvents["path"], TrafficEvents["part_path"], str(index_folder))
out_dir = os.path.join(TrafficEvents["path"], TrafficEvents["part_path"], "_" + str(index_folder))
print(dir)
print(out_dir)
if not os.path.exists(dir):
    print("does not exists {}".format(dir))
    raise("does not exists")
    
if not os.path.exists(out_dir):
     os.mkdir(out_dir)

for file_index in range(index_start_point_file, index_end_point_file):
    print("file_index: {}".format(file_index))
    file_url = dir + "/file_{}.csv".format(file_index)
    
    traffic_events_data = read_big_data_by_filter_with_key_values(file_url, traffic_filters)
    
    nearst_nodes_of_start_point = []
    nearst_nodes_of_end_point = []
    nearst_node_ids_of_start_validate_point = []
    nearst_node_ids_of_end_validate_point = []
    print("start file in {}".format(datetime.now()))
    for index, data in traffic_events_data.iterrows():
        start_location = Location([data["StartPoint_Lng"], data["StartPoint_Lat"]])
        if "EndPoint_Lng" in data and "EndPoint_Lat" in data and not math.isnan(data["EndPoint_Lat"]):
            end_location = Location([data["EndPoint_Lng"], data["EndPoint_Lat"]])
        else:
            end_location = Location([data["StartPoint_Lng"], data["StartPoint_Lat"]])

        nearst_nodes_start_location = OSRM.get_all_nearest_nodes_of_location(start_location, number_of_nearest_node)
        nearst_nodes_end_location = OSRM.get_all_nearest_nodes_of_location(end_location, number_of_nearest_node)
    
    
        nearst_way_points_start_location = []
        start_ids = []
        for point in nearst_nodes_start_location["waypoints"]:
            way_point = WayPoint(point)
            if way_point.validate_way_point():
                nearst_way_points_start_location.append(way_point)
                start_ids.extend(way_point.nodes)

        nearst_way_points_end_location = []
        end_ids = []
        for point in nearst_nodes_end_location["waypoints"]:
            way_point = WayPoint(point)
            if way_point.validate_way_point():
                nearst_way_points_end_location.append(way_point)
                end_ids.extend(way_point.nodes)
            

        nearst_nodes_of_start_point.append(nearst_nodes_start_location)
        nearst_nodes_of_end_point.append(nearst_nodes_end_location)

        nearst_node_ids_of_start_validate_point.append(start_ids)
        nearst_node_ids_of_end_validate_point.append(end_ids)
    
        if len(nearst_node_ids_of_start_validate_point) % 100 == 99:
            print(datetime.now())
            print(len(nearst_nodes_of_start_point))
            print("=======")
    traffic_events_data["nearst_nodes_of_start_point"] = nearst_nodes_of_start_point
    traffic_events_data["nearst_nodes_of_end_point"] = nearst_nodes_of_end_point
    traffic_events_data["nearst_nodes_ids_of_start_point"] = nearst_node_ids_of_start_validate_point
    traffic_events_data["nearst_nodes_ids_of_end_point"] = nearst_node_ids_of_end_validate_point
    
    output_file_url = out_dir + "/{}_file_{}.csv".format(file_index, file_index)
    traffic_events_data.to_csv (output_file_url, index = False, header=True)
    print(traffic_events_data.columns)
        
print("end")