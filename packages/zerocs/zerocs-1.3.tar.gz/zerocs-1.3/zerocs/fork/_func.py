"""
@time 2023-4-2
@auther YanPing
"""
import logging
import os
import json
import multiprocessing
from multiprocessing import Process

from nameko.standalone.rpc import ClusterRpcProxy

from zerocs.mate import _Mate
from zerocs.rabbitmq import RabbitMq
from zerocs.network import Network
from zerocs.logger import Logger


def run_task(json_data, service, config, res):
    res.append(1)
    service_path = os.getenv('ZERO_FW_SERVICE_PATH')
    module = __import__(f"{service_path}.{service}.{service}",
                        globals=globals(), locals=locals(), fromlist=['WorkFunction'])
    func = module.WorkFunction
    func(service, config, json_data)
    res.pop(0)


class _Func(RabbitMq, Network, Logger, _Mate):

    @staticmethod
    def rpc_proxy():
        _config = os.getenv('ZERO_FW_RABBITMQ_CONFIG')
        rpc_obj = ClusterRpcProxy({'AMQP_URI': _config}).start()
        return rpc_obj.zerocs_service

    def _log(self, msg):
        _path = os.getenv('ZERO_PROJECT_PATH')
        _file = os.getenv('ZERO_FW_LOGS_PATH')
        log_path = os.path.join(_path, _file)
        logger_ = self._logger(self._get_snowflake_id(datacenter_id=0, worker_id=0, did_wid=-1),
                               log_path, self.service_name)
        logger_.error(msg)

    def _container_start(self, container):
        container.start()
        container.wait()

    def _mq_callback(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        max_work = self.rpc_proxy().get_max_work(self._node_ip, self.service_name)
        _max_work = int(max_work) if max_work is not None else 1
        self._log(f'max_work == {_max_work}, res.len == {len(self._res)}')
        task_data = json.loads(body.decode())
        task_id = task_data['task_id']
        all_task_id = self.rpc_proxy().get_task_id(self.service_name, task_id)
        if task_id in all_task_id:
            logging.error(f'task is stop: {task_id}')
        else:
            if len(self._res) < _max_work:

                p = Process(target=run_task, args=(task_data, self.service_name, self._config, self._res,))
                p.start()
            else:
                ch.basic_publish(body=body, exchange='', routing_key=self.service_name)

    def _start_work(self, service_name, config):
        self._config = config
        self._node_ip = self._get_ipaddr()
        self.service_name = service_name
        self._res = multiprocessing.Manager().list()
        self._rabbitmq_init(config)
        self._get_message(service_name, self._mq_callback)
