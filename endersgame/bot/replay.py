import csv
from datetime import datetime
from collections import defaultdict

from endersgame.bot.streams import StreamBatch, StreamPoint


# Define a data structure for each row
class MarketDataPoint:
    def __init__(self, row):
        self.securityId = row["securityId"]
        self.bid = float(row["bid"])
        self.mid = float(row["mid"])
        self.offer = float(row["offer"])
        self.bid_size = float(row["bid_size"])
        self.offer_size = float(row["offer_size"])
        self.dest = row["dest"]
        self.utc = int(row["utc"])
        self.dt = datetime.fromtimestamp(int(row["utc"])/1000)

    def __repr__(self):
        return f"{self.securityId} - Bid: {self.bid}, Offer: {self.offer}"

    def get_field_value(self, field):
        return getattr(self, field, None)

# Read and group data by UTC time
def read_and_group_by_time(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        data_by_time = defaultdict(list)

        for row in reader:
            data_point = MarketDataPoint(row)
            data_by_time[data_point.utc].append(data_point)

    return data_by_time



class Replay:
    def __init__(self, file_name: str, field: str, substream_ids_only: list[str] = None):
        self.file_name = file_name
        self.field = field
        self.substream_ids_only  = set(substream_ids_only) if substream_ids_only else None
        self.data = read_and_group_by_time(file_name)
        self.timestamps = sorted(self.data.keys())
        self.idx = 0

    def filter(self, pt: MarketDataPoint):
        if self.substream_ids_only:
            return pt.securityId in self.substream_ids_only
        return True

    def tick(self) -> StreamBatch:
        if self.idx >= len(self.timestamps):
            return None

        current_time = self.timestamps[self.idx]
        points = (
            StreamPoint(substream_id=pt.securityId,
                        t=pt.dt,
                        value=pt.get_field_value(self.field))
            for pt in self.data[current_time] if self.filter(pt))
        self.idx += 1
        return StreamBatch(points=points)
