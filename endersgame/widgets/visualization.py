import matplotlib.pyplot as plt
import numpy as np
from collections import deque
from IPython.display import display
from typing import Deque

from endersgame.widgets.streams import Prediction, StreamPoint

import warnings

# Suppress the specific UserWarning
warnings.filterwarnings("ignore", message=".*Attempting to set identical low and high xlims.*")

# Define margin adjustment functions
def margin_down(y: float, margin: float = 0.005) -> float:
    return y * (1 + margin) if y < 0 else y * (1 - margin)

def margin_up(y: float, margin: float = 0.005) -> float:
    return y * (1 - margin) if y < 0 else y * (1 + margin)

# Define optimized TimeSeriesVisualizer class
class TimeSeriesVisualizer:
    def __init__(self, max_points: int = 200, update_interval: int = 10):
        self.max_points = max_points
        self.update_interval = update_interval

        # Disable automatic figure rendering
        plt.ioff()

        # Initialize figure and axis
        self.fig, self.ax = plt.subplots()
        self._setup_plot_style()

        # Initialize deques to store time and value data
        self.times: Deque[int] = deque(maxlen=max_points)
        self.values: Deque[float] = deque(maxlen=max_points)
        self.prediction_times: Deque[int] = deque(maxlen=max_points)
        self.predictions: Deque[float] = deque(maxlen=max_points)

        # Initialize plot elements
        self.line, = self.ax.plot([], [], color='lightgrey', label='Realized')
        self.scatter = self.ax.scatter([], [], c=[], marker='o', label='Predicted')

        # Set up legend
        self.ax.legend()

        # Internal variable to track display handle in Jupyter
        self.display_handle = None

        # Counter for updates
        self.update_counter = 0

    def _setup_plot_style(self):
        """Set up the plot style."""
        plt.style.use('dark_background')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.set_xlabel('Time', color='white')
        self.ax.set_ylabel('Value', color='white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')

    def process(self, data: StreamPoint, prediction: Prediction):
        """Update the plot with new data from StreamPoint."""
        # Append new data to deques
        self.times.append(data.ndx)
        self.values.append(data.value)
        self.prediction_times.append(prediction.ndx)
        self.predictions.append(prediction.value)

        self.update_counter += 1

        # Update plot at specified intervals
        if self.update_counter % self.update_interval == 0:
            self._update_plot()

    def _update_plot(self):
        """Update the plot with current data."""
        # Convert deques to numpy arrays for efficient plotting
        times_array = np.array(self.times)
        values_array = np.array(self.values)
        prediction_times_array = np.array(self.prediction_times)

        # Update realized values line
        self.line.set_data(times_array, values_array)

        # Update predicted values scatter plot
        colors = ['lime' if p > 0 else 'red' if p < 0 else 'white' for p in self.predictions]
        self.scatter.set_offsets(np.column_stack((prediction_times_array, values_array)))
        self.scatter.set_color(colors)

        # Adjust axis limits
        all_times = np.concatenate((times_array, prediction_times_array))
        self.ax.set_xlim(margin_down(np.min(all_times)), margin_up(np.max(all_times)))
        self.ax.set_ylim(margin_down(np.min(values_array)), margin_up(np.max(values_array)))

        # Redraw the plot
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

        # Update display in Jupyter
        if self.display_handle is None:
            self.display_handle = display(self.fig, display_id=True)
        else:
            self.display_handle.update(self.fig)

    def clear(self):
        """Clear the plot and reset data."""
        self.times.clear()
        self.values.clear()
        self.prediction_times.clear()
        self.predictions.clear()
        self.line.set_data([], [])
        self.scatter.set_offsets([])
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

if __name__ == "__main__":
    import time

    # Example usage
    visualizer = TimeSeriesVisualizer(max_points=200, update_interval=10)

    # Simulate data stream
    for i in range(1000):
        data = StreamPoint(ndx=i, value=np.sin(i/50) + np.random.normal(0, 0.1))
        prediction = Prediction(ndx=i+1, value=np.random.choice([-1, 0, 1]))
        visualizer.process(data, prediction)
        time.sleep(0.01)  # Simulate real-time data arrival

    plt.show()
