import matplotlib.pyplot as plt
from IPython.display import display
from typing import List
from endersgame.crunch.websocket import StreamPoint, Prediction

# Define margin adjustment functions
def margin_down(y: float, margin: float = 0.005) -> float:
    return y * (1 + margin) if y < 0 else y * (1 - margin)

def margin_up(y: float, margin: float = 0.005) -> float:
    return y * (1 - margin) if y < 0 else y * (1 + margin)

# Define TimeSeriesVisualizer class
class TimeSeriesVisualizer:
    def __init__(self, max_points: int = 200):
        self.max_points = max_points
        # Disable automatic figure rendering
        plt.ioff()

        # Do not create the figure immediately
        self.fig = None
        self.ax = None

        # Initialize lists to store time and value data
        self.times: List[int] = []
        self.values: List[float] = []
        self.prediction_times: List[int] = []
        self.predictions: List[float] = []

        # Internal variable to track display handle in Jupyter
        self.display_handle = None

        # Set a modern dark style
        plt.style.use('dark_background')  # Use a built-in style that looks good with grey tones

    def _initialize_plot(self):
        """Create the figure and axes when needed."""
        if self.fig is None or self.ax is None:
            self.fig, self.ax = plt.subplots()
            self.ax.set_facecolor('#2b2b2b')  # Set the background to a dark grey
            self.ax.set_xlabel('Time', color='white')  # Set axis label color to white
            self.ax.set_ylabel('Value', color='white')  # Set axis label color to white
            self.ax.tick_params(axis='x', colors='white')  # X ticks color
            self.ax.tick_params(axis='y', colors='white')  # Y ticks color

    def process(self, data: StreamPoint, prediction: Prediction):
        """Update the plot with new data from StreamPoint."""
        # Initialize the plot if it's the first time we are processing data
        self._initialize_plot()

        # Append new data to lists
        self.times.append(data.n)
        self.values.append(data.value)
        self.prediction_times.append(prediction.n)
        self.predictions.append(prediction.value)

        # Trim the data to the maximum number of points
        if len(self.times) > self.max_points:
            self.times = self.times[-self.max_points:]
            self.values = self.values[-self.max_points:]

        if len(self.prediction_times) > self.max_points:
            self.prediction_times = self.prediction_times[-self.max_points:]
            self.predictions = self.predictions[-self.max_points:]

        # Clear the previous plot
        self.ax.cla()
        self.ax.set_facecolor('#2b2b2b')  # Set background again after clearing
        self.ax.set_xlabel('Time', color='white')  # Set axis label color to white
        self.ax.set_ylabel('Value', color='white')  # Set axis label color to white
        self.ax.tick_params(axis='x', colors='white')  # X ticks color
        self.ax.tick_params(axis='y', colors='white')  # Y ticks color

        # Plot realized values as a line plot
        self.ax.plot(self.times, self.values, color='lightgrey', label='Realized')  # Light grey line

        # Plot predicted values with different markers
        for pt, pv, val in zip(self.prediction_times, self.predictions, self.values):
            marker, color = ('^', 'lime') if pv > 0 else ('v', 'red') if pv < 0 else ('o', 'white')
            self.ax.scatter(pt, val, color=color, marker=marker, label='Predicted')

        # Adjust axis limits
        all_times = self.times + self.prediction_times
        self.ax.set_xlim(margin_down(min(all_times)), margin_up(max(all_times)))
        self.ax.set_ylim(margin_down(min(self.values)), margin_up(max(self.values)))

        # Redraw the plot in the existing figure
        if self.display_handle is not None:
            # If the display handle already exists, update the figure in the same output cell
            self.display_handle.update(self.fig)
        else:
            # If this is the first time, create a display handle to track the figure
            self.display_handle = display(self.fig, display_id=True)

        # Close the figure to prevent Jupyter from displaying it a second time
        plt.close(self.fig)

    def clear(self):
        """Clear the plot and close the figure."""
        if self.ax:
            self.ax.cla()
        if self.fig:
            plt.close(self.fig)
