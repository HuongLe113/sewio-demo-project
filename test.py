import asyncio
import jmespath
import json
import websockets

async def hello():
    async with websockets.connect("ws://192.168.225.2") as websocket:
        await websocket.send('{"headers":{"X-ApiKey":"171555a8fe71148a165392904"},"method":"subscribe", "resource":"/feeds/9"}')
        response = await websocket.recv()
        data = json.loads(response)
        data = jmespath.search("body.[(datastreams[?id=='posX'].current_value | [0]), (datastreams[?id=='posY'].current_value | [0])]", data)
        data[0], data[1] = float(data[0]), float(data[1])
        return data

data = asyncio.run(hello())

# data = asyncio.get_event_loop().run_until_complete(hello())
print(data)