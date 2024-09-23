import matplotlib.pyplot as plt
from IPython.display import display
from typing import List
from endersgame.bot.bot import StreamPoint, Prediction

# Define margin adjustment functions
def margin_down(y: float, margin: float = 0.1) -> float:
    return y * (1 + margin) if y < 0 else y * (1 - margin)

def margin_up(y: float, margin: float = 0.1) -> float:
    return y * (1 - margin) if y < 0 else y * (1 + margin)

# Define TimeSeriesVisualizer class
class TimeSeriesVisualizer:
    def __init__(self):
        # Use a style for the plot (can be customized)
        plt.style.use('seaborn-dark')

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

    def _initialize_plot(self):
        """Create the figure and axes when needed."""
        if self.fig is None or self.ax is None:
            self.fig, self.ax = plt.subplots()
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Value')

    def process(self, data: StreamPoint, prediction: Prediction):
        """Update the plot with new data from StreamPoint."""
        # Initialize the plot if it's the first time we are processing data
        self._initialize_plot()

        # Append new data to lists
        self.times.append(data.n)
        self.values.append(data.value)
        self.prediction_times.append(prediction.n)
        self.predictions.append(prediction.value)

        # Clear the previous plot
        self.ax.cla()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')

        # Plot realized values as a line plot
        self.ax.plot(self.times, self.values, color='b', label='Realized')

        # Plot predicted values with different markers
        for pt, pv, val in zip(self.prediction_times, self.predictions, self.values):
            marker, color = ('^', 'g') if pv > 0 else ('v', 'r') if pv < 0 else ('o', 'k')
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

        plt.draw()

    def clear(self):
        """Clear the plot and close the figure."""
        if self.ax:
            self.ax.cla()
        if self.fig:
            plt.close(self.fig)
