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

    def replay(self, filename: str = "currency.csv", delay: float = 0.01, only: str = 'GBP/USD'):
        """ Replay data from a file."""
        self.setup()
        data = Replay(filename, "mid", substream_ids_only=[only])
        for point in data.values(delay=delay):
            prediction = self.predict_func(point.value, self.k)
            self.postprocess(point, Prediction(value=prediction, t=point.t, n=point.n + self.k))

    def live(self):
        """ Live data from a stream."""
        self.setup()

        bot = Websocket("http://localhost:8989")
        bot.login(user_id='antoine')
        bot.register(stream='currency')
        bot.connect()
        print("Connected to stream")

        # Define a signal handler to stop the process gracefully
        def signal_handler(sig, frame):
            print("Interrupt received, disconnecting...")
            self.stop_event.set()  # Set the event to stop the live feed
            bot.disconnect()
            print("Disconnected from stream")

        # Register the signal handler to listen for Ctrl+C
        signal.signal(signal.SIGINT, signal_handler)

        # Run the live feed in a separate thread to handle values
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
                bot.disconnect()
                print("Live feed stopped")

        # Create and start the live thread
        live_thread = threading.Thread(target=run)
        live_thread.start()

        # Wait for the thread to finish (on interrupt or natural completion)
        live_thread.join()
        print("Live data processing complete")
