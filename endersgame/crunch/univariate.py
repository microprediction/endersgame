import signal
import sys
import threading
from platform import system
from typing import Iterator

from IPython.core.display_functions import clear_output

from endersgame.crunch.websocket import Websocket
from endersgame.crunch.replay import Replay
from endersgame.crunch.streams import StreamPoint, Prediction
from endersgame.crunch.visualization import TimeSeriesVisualizer
from endersgame.crunch.accounting import AccountingDataVisualizer
from endersgame.accounting.simplepnl import SimplePnL



class Crunch:
    def __init__(self):
        """ Role of crunch is provide simple univariate wrappers around bot and replay."""
        self.predict_func = None
        self.k = 5
        self.accounting = None
        self.viz = None
        self.stop_event = threading.Event()

    def setup(self):
        from __main__ import predict_one
        self.predict_func = predict_one
        self.accounting = AccountingDataVisualizer(SimplePnL)
        self.viz = TimeSeriesVisualizer()

    def postprocess(self, point: StreamPoint, prediction: Prediction):
        self.viz.process(point, prediction)
        self.accounting.process(point, prediction)

    def replay(self, filename: str = "currency.csv", delay: float = 0.01, only: str = 'AUD/USD'):
        """ Replay data from a file."""
        self.setup()
        data = Replay(filename, "mid", substream_ids_only=[only])
        for point in data.values(delay=delay):
            prediction = self.predict_func(point.value, self.k)
            self.postprocess(point, Prediction(value=prediction, t=point.t, n=point.n + self.k))

    def live(self):
        """Live data from a stream."""
        self.setup()

        bot = Websocket("http://localhost:8989")
        bot.login(user_id='antoine')
        bot.register(stream='currency')
        bot.connect()
        print("Connected to stream")

        # Use a threading Event for clean stopping
        self.stop_event = threading.Event()

        # Define the live feed runner function
        def run():
            try:
                for point in bot.values():
                    if self.stop_event.is_set():
                        break  # Stop processing if the stop event is set
                    prediction = self.predict_func(point.value, self.k)
                    self.postprocess(point, Prediction(value=prediction, t=point.t, n=point.n + self.k))
            except Exception as e:
                print(f"Error during live processing: {e}")
            finally:
                bot.disconnect()  # Ensure disconnection
                print("Disconnected from stream")

        # Start the live feed in a separate thread
        live_thread = threading.Thread(target=run)
        live_thread.start()

        try:
            # Monitor the live thread and check for cell interruption
            while live_thread.is_alive():
                live_thread.join(timeout=1)  # Poll for thread completion
        except KeyboardInterrupt:
            print("Cell interrupt detected. Stopping...")
            self.stop_event.set()  # Signal the thread to stop
            live_thread.join()  # Ensure the thread finishes
            print("Live data processing stopped")
