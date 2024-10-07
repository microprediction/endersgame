import pandas as pd
import time
from IPython.display import display
import ipywidgets as widgets
from typing import Dict
import warnings
from endersgame.accounting.pnl import Pnl
from endersgame.widgets.streams import StreamPoint, Prediction

# Suppress FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

custom_css = """
<style>
    .table { 
        width: 100%; 
        margin-bottom: 1rem; 
        background-color: #343a40; /* Dark grey background */
        color: #f8f9fa; /* Light font color */
        border-collapse: collapse;
    }
    .table th, .table td {
        padding: 0.75rem;
        vertical-align: top;
        border-top: 1px solid #495057; /* Slightly lighter border */
    }
    .table thead th {
        vertical-align: bottom;
        border-bottom: 2px solid #495057; /* Slightly lighter header border */
        background-color: #495057; /* Darker grey for header */
        color: #f8f9fa; /* Light header text color */
    }
    .table tbody + tbody {
        border-top: 2px solid #495057; /* Slightly lighter bottom border */
    }
    .table-striped tbody tr:nth-of-type(odd) {
        background-color: #495057; /* Alternate row background */
    }
</style>
"""

# Dictionary mapping original column names to display names
display_names = {
    "stream_id": "Stream ID",
    "current_ndx": "Current Index",
    "num_resolved_decisions": "Resolved Decisions",
    "total_profit": "Total Profit",
    "wins": "Wins",
    "losses": "Losses",
    "win_loss_ratio": "Win/Loss Ratio",
    "profit_per_decision": "Profit/Decision",
    "standardized_profit_per_decision": "Standardized Profit/Decision",
    "average_profit_per_decision": "Average Profit/Decision",
    "avg_profit_per_decision_std_ratio": "Avg Profit/Decision Std Ratio"
}

class AccountingDataVisualizer:
    def __init__(self):
        self.account_model = Pnl
        self.accountants = {}
        self.df = pd.DataFrame(columns=[
            "stream_id", "current_ndx", "num_resolved_decisions", "total_profit",
            "wins", "losses", "win_loss_ratio", "profit_per_decision", "standardized_profit_per_decision"
        ])
        self.output = widgets.Output()
        self.table_widget = widgets.HTML(value=self.data())
        display(self.table_widget)

    def data(self):
        table_html = self.df.drop(columns=['stream_id']).rename(columns=display_names).to_html(classes='table table-striped')
        # Convert DataFrame to HTML with classes for styling
        return custom_css + table_html

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
            self.table_widget.value = self.data()

    def clear(self):
        pass
