import pandas as pd
import time
from IPython.display import display
import ipywidgets as widgets
from typing import Dict
import warnings
from endersgame.bot.bot import StreamPoint, Prediction

# Suppress FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

class AccountingDataVisualizer:
    def __init__(self, Accountant):
        self.account_model = Accountant
        self.accountants = {}
        self.df = pd.DataFrame(columns=[
            "stream_id", "current_ndx", "num_resolved_decisions", "total_profit",
            "wins", "losses", "win_loss_ratio", "profit_per_decision", "standardized_profit_per_decision"
        ])
        self.output = widgets.Output()
        self.table_widget = widgets.HTML(value=self.df.to_html(classes='table table-striped'))
        display(self.table_widget)

    def process(self, point: StreamPoint, prediction: Prediction):
        if point.substream_id not in self.accountants:
            self.accountants[point.substream_id] = self.account_model()
        accountant = self.accountants[point.substream_id]
        accountant.tick(point.value, prediction.n - point.n, prediction.value)
        self.update_data(point.substream_id, accountant.summary())
        self.update_display()

    def update_data(self, stream_id: str, summary: Dict):
        if stream_id in self.df['stream_id'].values:
            self.df.loc[self.df['stream_id'] == stream_id, list(summary.keys())] = list(summary.values())
        else:
            new_row = {"stream_id": stream_id, **summary}
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)

    def update_display(self):
        with self.output:
            self.table_widget.value = self.df.to_html(classes='table table-striped')

    def clear(self):
        pass


# Simulate the summary function with multiple streams
def simulate_multi_stream_summary_function():
    import random
    streams = ["stream_1", "stream_2"]
    summaries = {}
    for stream_id in streams:
        summaries[stream_id] = {
            "current_ndx": random.randint(1, 100),
            "num_resolved_decisions": random.randint(1, 50),
            "total_profit": round(random.uniform(100, 1000), 2),
            "wins": random.randint(1, 20),
            "losses": random.randint(1, 20),
            "win_loss_ratio": round(random.uniform(0, 5), 2),
            "profit_per_decision": round(random.uniform(10, 50), 2),
            "standardized_profit_per_decision": round(random.uniform(5, 25), 2),
        }
    return summaries
