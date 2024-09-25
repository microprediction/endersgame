import asyncio
import json
import threading
from collections import defaultdict
from queue import Queue, Empty
from abc import abstractmethod, ABC
from typing import Iterator

import websockets
import requests
import nest_asyncio

from endersgame.crunch.replay import Replay
from endersgame.crunch.streams import StreamPoint, Prediction, StreamBatch


class Websocket:
    def __init__(self, base_url: str = "http://localhost:8000", k_horizon: int = 5, only: str = 'AUD/USD'):
        self.base_url = base_url
        self.token = None
        self.stream_token = None
        self.n = 0
        self.k_horizon = k_horizon
        self.substream_id_only = only
        self._values_queue = Queue()  # Use Queue to store points
        self._loop = None
        self._thread = None
        self.websocket = None

    def values(self) -> Iterator[StreamPoint]:
        """Yield processed values from the queue."""
        while True:
            try:
                # Get data from the queue with a timeout to prevent blocking indefinitely
                point = self._values_queue.get(timeout=1)
                yield point
            except Empty:
                # Continue looping if no data is in the queue
                continue

    def process(self, batch: StreamBatch):
        """Process each point in the StreamBatch."""
        try:
            for point in batch.points:
                if point.substream_id != self.substream_id_only:
                    continue  # Skip points that don't match the specified substream_id
                point.n = self.n
                # Add the processed point to the queue for consumption
                self._values_queue.put(point)
            self.n += 1
        except Exception as e:
            print("Error processing data:", batch)
            print(e)

    # Websockets

    def login(self, user_id: str):
        try:
            url = f"{self.base_url}/login"
            data = {"user_id": user_id}
            response = requests.post(url, json=data)
            response.raise_for_status()
            self.token = response.json().get("token")
            print("Login successful")
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
            print("Stream registered")
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

    def _run_event_loop(self, url: str):
        nest_asyncio.apply()
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._listen(url))

    def connect(self):
        if not self.stream_token:
            raise ValueError("Please register first")
        try:
            ws_base_url = self.base_url.replace("http", "ws")
            ws_url = f"{ws_base_url}/ws?stream_token={self.stream_token}"
            self._thread = threading.Thread(target=self._run_event_loop, args=(ws_url,))
            self._thread.start()
            print("WebSocket connection started")
        except Exception as e:
            print("Error connecting to websocket:", e)

    def disconnect(self):
        if self.websocket and self.websocket.open:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self._loop).result()
            print("WebSocket connection has been closed")
        if self._thread:
            self._thread.join()
