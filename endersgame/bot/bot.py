import asyncio
import json
from collections import defaultdict
import time
from abc import abstractmethod, ABC

import websockets
import requests
import nest_asyncio

from endersgame.bot.replay import Replay
from endersgame.bot.streams import StreamPoint, Prediction, StreamBatch


class Sink(ABC):
    @abstractmethod
    def process(self, data: StreamPoint, prediction: Prediction):
        pass

    @abstractmethod
    def clear(self):
        pass

class Model(ABC):
    @abstractmethod
    def tick_and_predict(self, y: float, k:int=None)->float:
        pass

class Handler:
    def __init__(self):
        self.sinks = {}
        self.model = None

class Bot:
    def __init__(self, base_url: str = "http://localhost:8000", k_horizon:int=5, model: type[Model] = None):
        self.base_url = base_url
        self.token = None
        self.stream_token = None
        self.default_model = model
        self.handlers = defaultdict(Handler)

        self.n = 0
        self.k_horizon = k_horizon

    def with_model(self, substream_id: str, model: Model):
        self.handlers[substream_id].model = model

    def with_substream_sink(self, substream_id: str, sink: Sink):
        self.handlers[substream_id].sinks[type(sink).__name__] = sink

    def process(self, batch: StreamBatch):
        try:
            for point in batch.points:
                if point.substream_id not in self.handlers:
                    if not self.default_model:
                        continue
                    self.handlers[point.substream_id].model = self.default_model()
                handler = self.handlers[point.substream_id]
                point.n = self.n
                # TODO: We can use clean up data, order, call different methods later
                # Right now: relative times
                prediction = handler.model.tick_and_predict(point.value, self.k_horizon)
                for sink in handler.sinks.values():
                    sink.process(point, Prediction(value=prediction, t=point.t, n=self.n + self.k_horizon))
            self.n+=1
        except Exception as e:
            print("Error processing data:", batch)
            print(e)

    # Replay
    def run(self, replay: Replay, delay=0.5):
        while True:
            batch = replay.tick()
            if not batch:
                break
            self.process(batch)
            time.sleep(delay)

    # Websockets

    def login(self, user_id: str):
        try:
            url = f"{self.base_url}/login"
            data = {"user_id": user_id}
            response = requests.post(url, json=data)
            response.raise_for_status()
            self.token = response.json().get("token")
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def register(self, stream: str, ids_only: list[str] = None):
        if not self.token:
            raise ValueError("Please login first")
        try:
            url = f"{self.base_url}/register_stream"
            data = {"token": self.token, "stream": stream, "ids_only": ids_only}
            response = requests.post(url, json=data)
            self.stream_token = response.json().get("stream_token")
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    async def _listen(self, url: str):
        async with websockets.connect(url) as websocket:
            # Check if the WebSocket is open
            if not websocket.open:
                print("WebSocket connection is closed")
                return
            self.websocket = websocket
            while websocket.open:
                try:
                    message = await websocket.recv()
                    batch = StreamBatch.parse_obj(json.loads(message))
                    self.process(batch)
                except json.JSONDecodeError:
                    print("Invalid JSON data:", message)
                except websockets.ConnectionClosedOK:
                    print("Connection closed normally.")
                    break
                except websockets.ConnectionClosedError:
                    print("Connection closed with an error.")
                    break
                except Exception as e:
                    print("Error processing data:", message)
                    print(e)

            print("WebSocket connection is closed")

    def connect(self):
        if not self.stream_token:
            raise ValueError("Please register first")
        try:
            ws_base_url = self.base_url.replace("http", "ws")
            print("Connecting to", ws_base_url)
            ws_url = f"{ws_base_url}/ws?stream_token={self.stream_token}"
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            loop.create_task(self._listen(ws_url))
        except Exception as e:
            print("Error connecting to websocket:", e)

    def disconnect(self):
        if self.websocket and self.websocket.open:
            asyncio.run(self.websocket.close())
            print("WebSocket connection has been closed")
        for handler in self.handlers.values():
            for sink in handler.sinks.values():
                sink.clear()
