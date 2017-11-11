from typing import List
from collections import Counter
from pprint import pprint

from utils import skipped_actions


class StressTestReport:
    """
    Class for aggregation stress test metrics and report generation
    """
    def __init__(self, metrics: List, rest_actions_info):
        self._metrics = metrics
        self._rest_actions_info = rest_actions_info

    def process_metrics(self):
        am_sums = Counter()
        am_counters = Counter()
        err_sums = Counter()
        for action_metrics, error_metrics in self._metrics:
            action_metrics = {
                key: value for key, value in action_metrics.items()
                if key not in skipped_actions
            }
            am_sums.update(action_metrics)
            am_counters.update(action_metrics.keys())
            err_sums.update(error_metrics)

        print("Action metrics (averages):")
        pprint({metric: float(am_sums[metric])/am_counters[metric]
                for metric in am_sums.keys()}, indent=4)

        print("Error metrics:")
        pprint(
            dict(
                map(
                    lambda t:
                    (t[0], '%2.2f%%'
                     % ((t[1] / self._rest_actions_info[t[0]]) * 100)),
                    err_sums.items())
            )
            , indent=4
        )

# TODO implement JMEter like report
