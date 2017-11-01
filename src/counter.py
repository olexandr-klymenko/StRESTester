from typing import Tuple, AnyStr
from collections import defaultdict

__all__ = ['StatsCounter']


class StatsCounter:
    """
    Class for dealing with stress test scenario actions' metrics
     within separate process.
    It collects them and finally returns to for StressTestReport to process
    """
    _time_counter = {}
    _error_counter = defaultdict(int)

    @classmethod
    def append_time_metric(cls, metric: Tuple):
        action_name, timed_value = metric
        cls._time_counter.setdefault(action_name, []).append(timed_value)

    @classmethod
    def append_error_metric(cls, action_name: AnyStr):
        cls._error_counter[action_name] += 1

    @classmethod
    def get_averages(cls):
        return {action_name: sum(values) / len(values)
                for action_name, values in cls._time_counter.items()}

    @classmethod
    def get_errors(cls):
        return dict(cls._error_counter)

    @classmethod
    def get_total_time(cls):
        return sum(sum(metric) for metric in cls._time_counter.values())
