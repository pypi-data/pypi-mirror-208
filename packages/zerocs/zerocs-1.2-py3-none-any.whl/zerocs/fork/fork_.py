"""
@time 2023-4-2
@auther YanPing
"""
from multiprocessing import Process
from ._func import _Func


class Func(_Func):

    def container_fork(self, container):
        """
        container start
        :param container:  container obj
        :return:
        """
        super()._container_start(container)

    def work_fork(self, service_name, config):
        """
        Start Work
        :param service_name: service name
        :param config: rabbitmq config
        :return:
        """
        self._start_work(service_name, config)


class Fork:

    @staticmethod
    def _container_fork(container):
        """
        container obj fork
        :param container: container obj
        :return:
        """

        p = Process(target=Func().container_fork, args=(container,))
        p.start()
        return p.pid

    @staticmethod
    def _work_fork(service_name, config):
        """
        work obj fork
        :param service_name: service name
        :return:
        """
        p = Process(target=Func().work_fork, args=(service_name, config,))
        p.start()
        return p.pid
