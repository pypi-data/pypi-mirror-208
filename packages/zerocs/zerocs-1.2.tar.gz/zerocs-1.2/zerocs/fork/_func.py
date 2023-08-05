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


def run_task(json_data, service, config, res):
    res.append(1)
    service_path = os.getenv('ZERO_FW_SERVICE_PATH')
    module = __import__(f"{service_path}.{service}.{service}",
                        globals=globals(), locals=locals(), fromlist=['WorkFunction'])
    func = module.WorkFunction
    func(service, config, json_data)
    res.pop(0)


class _Func(RabbitMq, _Mate):

    @staticmethod
    def rpc_proxy():
        _config = os.getenv('ZERO_FW_RABBITMQ_CONFIG')
        rpc_obj = ClusterRpcProxy({'AMQP_URI': _config}).start()
        return rpc_obj.zerocs_service

    def _container_start(self, container):
        container.start()
        container.wait()

    def _mq_callback(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        max_work = os.getenv(f'{self.service_name}_MAX_WORK')
        _max_work = int(max_work) if max_work is not None else 1
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
        self.service_name = service_name
        self._res = multiprocessing.Manager().list()
        self._rabbitmq_init(config)
        self._get_message(service_name, self._mq_callback)
