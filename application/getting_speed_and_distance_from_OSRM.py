import pandas as pd
import requests 
import os
import math
from xml.etree import ElementTree
from datetime import datetime

TrafficEvents = None

OSRM_BASIC_URL = "https://usaeta.bluebitsoft.com/"
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

class Location(object):
    def __init__(self, latitude, longitude):
        self.longitude = longitude
        self.latitude = latitude

class OSRM(object):
    @staticmethod
    def get_all_nearest_nodes_of_location(location, number=1):
        params = {
            "number": number
        }
        URL = OSRM_BASIC_URL + "nearest/v1/driving/{},{}".format(location.longitude, location.latitude)
        response = requests.get(url = URL, params = params)
        return response.json() 
    
    @staticmethod
    def get_eta_and_distance(origin, destination):
        try:
            URL = OSRM_BASIC_URL + "route/v1/driving/{},{};{},{}".format(
                origin.longitude, origin.latitude, destination.longitude, destination.latitude)
            #print(URL)
            response = requests.get(url = URL)
            result = response.json()
            routes = result["routes"]
#             print("routes: {}".format(routes))
            route = routes[0]
            eta = route["duration"]
            #print("eta : {}".format())
            distance = route["distance"]
            speed = distance / eta
            # print("eta : {}, distance : {}, speed : {}".format(eta, distance, speed))
        except:
            eta = -100
            distance = -100
            speed = -100
        return eta, distance, speed


out_dir = BASE_PATH + "speed" +"_" + str(index_folder)
if not os.path.exists(out_dir):
     os.mkdir(out_dir)

for i in range(index_start_point_file, index_end_point_file):
    print("file id is {}".format(i))
    print("start time is {}".format(datetime.now()))
    path = BASE_PATH + "_" + str(index_folder) + "_" + "/" + str(i) + "_file_"+ str(i) + ".csv"
    
    print(path)
    speeds = []
    distances = []
    etas = []
    traffic_events_data = read_data(path)
    for index, data in traffic_events_data.iterrows():
        speed = -100
        distance = -100
        eta = -100
        start_location = Location(data["StartPoint_Lat"], data["StartPoint_Lng"])
        if "EndPoint_Lng" in data and "EndPoint_Lat" in data and not math.isnan(data["EndPoint_Lat"]):
            end_location = Location(data["EndPoint_Lat"], data["EndPoint_Lng"])
            eta, distance, speed = OSRM.get_eta_and_distance(start_location, end_location)
        
        speeds.append(speed)
        etas.append(eta)
        distances.append(distance)
        if index % 100 == 0:
            print("number: {} with code {}, has {} speed, {} eta, {} distance".format(index, data["Id"], speed, eta, distance))
            print("Time is {}".format(datetime.now()))
    
    traffic_events_data["avg_speed"] = speeds
    traffic_events_data["distance"] = distances
    traffic_events_data["eta"] = etas 
    
    output_file_url = out_dir + "/" + str(i) + "_file_"+ str(i) + ".csv"
    traffic_events_data.to_csv (output_file_url, index = False, header=True)
    print(traffic_events_data.columns)
    print("{} done".format(output_file_url))
    print("end time is {}".format(datetime.now()))

