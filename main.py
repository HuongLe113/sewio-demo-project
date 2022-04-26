import jmespath
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import style
import json
import websockets
import asyncio
import requests


class Sewio:
    BASE_API_URL = "http://192.168.225.2/sensmapserver/api"
    ANCHORS_API_URL = f"{BASE_API_URL}/anchors"
    COLOR_DRAW = [
        '-bo', # 1 BLUE
        '-ro', # 2 RED
        '-co', # 3 CYAN
        '-mo', # 4 MAGENTA
        '-yo', # 5 YELLOW
    ]
    def __init__(self, api_key="17254faec6a60f58458308763", tag_ids=None):
        self.api_key = api_key
        self.figure = plt.figure()
        self.tag_ids = tag_ids
        self.plot_map = self.figure.add_subplot(1, 1, 1)
        style.use('fivethirtyeight')
        self.anchor_data = self.get_anchors_pos()
        self.tag_data = {}
        self.color_tags = {}
        for ind, tag_id in enumerate(self.tag_ids): # TOI DA 5 TAG
            self.color_tags[tag_id] = self.COLOR_DRAW[ind]
    
    async def get_tag_pos(self, tag_id):
        async with websockets.connect("ws://192.168.225.2") as websocket:
            await websocket.send('{"headers":{"X-ApiKey":"171555a8fe71148a165392904"},"method":"subscribe", "resource":"/feeds/' + str(tag_id) + '"}')
            response = await websocket.recv()
            data = json.loads(response)
            data = jmespath.search("body.[(datastreams[?id=='posX'].current_value | [0]), (datastreams[?id=='posY'].current_value | [0])]", data)
            if data and data[0] and data[1]:
                data[0], data[1] = float(data[0]), float(data[1])
                return data
            return None

    def get_anchors_pos(self):
        headers = {
            "accept": "application/json",
            "X-ApiKey": self.api_key,
        }
        response = requests.get(self.ANCHORS_API_URL, headers=headers)

        if response.status_code != 200:
            raise Exception("[Error]: Got a error when calling get {name}")
        
        data = response.json()
        data = jmespath.search("results[*].[(datastreams[?id=='posX'].current_value | [0]), (datastreams[?id=='posY'].current_value | [0])]", data)
        # print(response.elapsed.total_seconds())
        
        try:
            parsed_data = [[float(pos[0]) for pos in data], [float(pos[1]) for pos in data]]
        except(Exception):
            raise Exception("[Error]: Got a error when parsing data")
        
        return parsed_data
        
    def plot_pos_data(self, i):
        # tag_data = self.get_tag_pos()
        for tag_id in self.tag_ids:
            """

            tag_pos = [12, 34]
            self.tag_data[tag_id][0] = [1 , 2, 3, 4]
            self.tag_data[tag_id][1] = [5, 6, 7, 8]
            => 
            self.tag_data[tag_id][0] = [1 , 2, 3, 4, 12]
            self.tag_data[tag_id][1] = [5, 6, 7, 8, 34]
            """
            tag_pos = asyncio.run(self.get_tag_pos(tag_id))
            if tag_pos:
                if self.tag_data.get(tag_id):
                    self.tag_data[tag_id][0].append(tag_pos[0])
                    self.tag_data[tag_id][1].append(tag_pos[1])
                else:
                    self.tag_data[tag_id] = [[tag_pos[0]], [tag_pos[1]]]
            # print(self.tag_data)
        self.plot_map.clear()
        self.plot_map.invert_yaxis()
        if self.anchor_data:
            self.plot_map.plot(self.anchor_data[0], self.anchor_data[1], "go", label="Anchors", markersize=4)

        for tag_id in self.tag_ids:
            if self.tag_data.get(tag_id):
                self.plot_map.plot(self.tag_data[tag_id][0], self.tag_data[tag_id][1], self.color_tags[tag_id], label="Tags", markersize=4, linewidth=1.5)
        
    def plot_animate(self):
        ani = animation.FuncAnimation(self.figure, self.plot_pos_data, interval=200)
        plt.show()
       

if __name__ == '__main__': 
    sewio = Sewio(tag_ids=[
        9, 
        10, 
        11, 
        12, 
        # 14,
    ])
    sewio.plot_animate()
