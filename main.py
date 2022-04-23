import jmespath
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import style
import requests

import random

class Sewio:
    BASE_API_URL = "https://demo.sewio.net/sensmapserver/api"
    ANCHORS_API_URL = f"{BASE_API_URL}/anchors"
    TAGS_API_URL = f"{BASE_API_URL}/tags"
    MAPPING_URL = {
        'anchors': ANCHORS_API_URL,
        'tags': TAGS_API_URL,
    }
    
    def __init__(self, api_key="171555a8fe71148a165392904"):
        self.api_key = api_key
        self.figure = plt.figure()
        self.plot_map = self.figure.add_subplot(1, 1, 1)
        style.use('fivethirtyeight')
        self.get_anchors_pos()
        self.get_tag_pos()
    
    def get_pos(self, name):
        api_url = self.MAPPING_URL[name]
        headers = {
            "accept": "application/json",
            "X-ApiKey": self.api_key,
        }
        req = requests.get(api_url, headers=headers)

        if req.status_code != 200:
            raise Exception("[Error]: Got a error when calling get {name}")
        
        data = req.json()
        data = jmespath.search("results[*].[(datastreams[?id=='posX'].current_value | [0]), (datastreams[?id=='posY'].current_value | [0])]", data)
        
        try:
            parsed_data = [[float(pos[0]) for pos in data], [float(pos[1]) for pos in data]]
        except(Exception):
            raise Exception("[Error]: Got a error when parsing data")
        
        print(parsed_data)
        return parsed_data
    
    def get_anchors_pos(self):
        self.anchor_data = self.get_pos("anchors")
        return self.get_pos("anchors")
    
    def get_tag_pos(self):
        self.tag_data = self.get_pos("tags")
        return self.get_pos("tags")
        
        
    def plot_pos_data(self, i):
        # anchor_data = self.get_anchors_pos()
        # tag_data = self.get_tag_pos()
        self.tag_data[0].append(random.uniform(1, 50))
        self.tag_data[1].append(random.uniform(1, 50))
        self.plot_map.clear()
        self.plot_map.plot(self.anchor_data[0], self.anchor_data[1], "go", label="Anchors", markersize=4)
        self.plot_map.plot(self.tag_data[0], self.tag_data[1], "-ro", label="Tags", markersize=4, linewidth=1.5)
        
    def plot_animate(self):
        ani = animation.FuncAnimation(self.figure, self.plot_pos_data, interval=1000)
        plt.show()
        
sewio = Sewio()
sewio.plot_animate()
