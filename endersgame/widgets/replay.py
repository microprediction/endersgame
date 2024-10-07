from typing import Iterable

from endersgame.widgets.accounting import AccountingDataVisualizer
from endersgame.widgets.streams import StreamPoint, Prediction
from endersgame.widgets.visualization import TimeSeriesVisualizer


def replay(streams: Iterable[Iterable[dict]]):
    try:
        from __main__ import infer
    except ImportError:
        print("Please define the 'infer' function in the main module.")
        return
    accounting = AccountingDataVisualizer()
    for stream_id, stream in enumerate(streams):
        viz = TimeSeriesVisualizer()
        prediction_generator = infer(stream)
        next(prediction_generator)
        for idx, data_point in enumerate(stream):
            prediction = next(prediction_generator)
            data = StreamPoint(substream_id=stream_id, value=data_point['x'], n=idx)
            pred = Prediction(value=prediction, n=idx)
            accounting.process(data, pred)
            viz.process(data, pred)
            if idx > 25:
                break
