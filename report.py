from typing import List
from collections import Counter


class StressTestReport:
    """
    Class for aggregation stress test metrics and report generation
    """
    def __init__(self, metrics: List):
        self._metrics = metrics

    def process_metrics(self):
        am_sums = Counter()
        am_counters = Counter()
        err_sums = Counter()
        for action_metrics, error_metrics in self._metrics:
            am_sums.update(action_metrics)
            am_counters.update(action_metrics.keys())
            err_sums.update(error_metrics)

        print("Action metrics (averages): %s"
              % {metric: float(am_sums[metric])/am_counters[metric] for metric in am_sums.keys()})
        print("Error metrics: %s" % dict(err_sums))

# TODO implement JMEter like report
