"""
@time 2023-4-2
@auther YanPing
"""
import os
import datetime
import logging
import traceback
from logging import handlers
from weakref import WeakKeyDictionary

from nameko.extensions import DependencyProvider

from zerocs.mate import _Mate


class _Logger(DependencyProvider, _Mate):
    __timestamps = WeakKeyDictionary()
    __format_str = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

    def _logger(self, snowflake_id, log_path, filename):
        self.__log = logging.getLogger(snowflake_id)
        self.__log.setLevel(logging.ERROR)
        if os.path.exists(log_path) is False:
            os.makedirs(log_path)
        th = handlers.TimedRotatingFileHandler(filename=f'{log_path}/{filename}',
                                               when='MIDNIGHT', backupCount=7, encoding='utf-8')
        th.suffix = "%Y-%m-%d.log"
        th.setFormatter(self.__format_str)
        self.__log.addHandler(th)
        return self.__log

    def worker_setup(self, worker_ctx):

        self.__timestamps[worker_ctx] = datetime.datetime.now()

        service_name = worker_ctx.service_name
        method_name = worker_ctx.entrypoint.method_name

        self.__log.info("Worker %s.%s starting", service_name, method_name)

    def worker_result(self, worker_ctx, result=None, exc_info=None):

        service_name = worker_ctx.service_name
        method_name = worker_ctx.entrypoint.method_name

        if exc_info is None:
            status = "completed"
        else:
            status = "errored"
            self.__log.error(traceback.print_tb(exc_info[2]))

        now = datetime.datetime.now()
        worker_started = self.__timestamps.pop(worker_ctx)
        elapsed = (now - worker_started).seconds

        self.__log.info("Worker %s.%s %s after %ss",
                        service_name, method_name, status, elapsed)
