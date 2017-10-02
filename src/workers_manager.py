import multiprocessing as mp
from multiprocessing import Queue

from report import StressTestReport
from utils import progress_handler, StressTestProcess
from worker import worker


class WorkerManager:
    def __init__(self, scenario_xml_root, workers_number, total_actions):
        self._scenario_xml_root = scenario_xml_root
        self._workers_number = workers_number
        self._total_actions = total_actions
        self._workers_info = {}
        self._report_metrics = []
        self._progress_queue = None
        self._progress_process = None

    def manage_workers(self):
        self._init_progress_queue()
        self._init_workers()
        self._start_workers()
        self._receive_metrics()
        self._join_workers()
        self._close_workers()

    def _init_progress_queue(self):
        self._progress_queue = mp.Queue()
        self._progress_process = mp.Process(target=progress_handler, args=(self._progress_queue,
                                                                           self._total_actions))
        self._progress_process.start()

    def _init_workers(self):
        for index in range(1, self._workers_number + 1):
            parent_conn, child_conn = mp.Pipe()
            self._workers_info[index] = parent_conn, StressTestProcess(target=worker,
                                                                       args=(index,
                                                                             self._scenario_xml_root,
                                                                             child_conn,
                                                                             self._progress_queue))

    def _start_workers(self):
        for _, (__, process) in self._workers_info.items():
            process.start()

    def _receive_metrics(self):
        for _, (parent_conn, __) in self._workers_info.items():
            self._report_metrics.append(parent_conn.recv())

    def _join_workers(self):
        for _, (__, process) in self._workers_info.items():
            process.join()

    def _close_workers(self):
        try:
            for _, (__, process) in self._workers_info.items():
                if process.exception:
                    error, traceback = process.exception
                    raise Exception(traceback)

        except Exception:
            self._progress_process.terminate()
            raise
        else:
            self._progress_process.join()
        finally:
            report = StressTestReport(self._report_metrics)
            report.process_metrics()
