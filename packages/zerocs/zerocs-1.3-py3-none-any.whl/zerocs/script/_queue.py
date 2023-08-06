"""
@time 2023-4-2
@auther YanPing
"""

import os
import eventlet

from nameko.containers import ServiceContainer

from zerocs.mate import _Mate
from zerocs.base.default_func_ import ServiceRegister, ZeroFWService, ZeroFWConfig

eventlet.monkey_patch()


class _Queue(ServiceRegister, _Mate):
    service_name = None

    def _get_func_module(self, service_name):
        service_path = os.getenv('ZERO_FW_SERVICE_PATH')
        module = __import__(f"{service_path}.{service_name}.{service_name}",
                            globals=globals(), locals=locals(), fromlist=['RpcFunction'])
        return module.RpcFunction

    def _get_container(self, service_name, config):
        cls = self._get_func_module(service_name)
        self._service_register(cls)
        service_id = cls.__dict__.get('name')
        container = ServiceContainer(cls, config={"AMQP_URI": config})
        return container, service_id

    def _get_container_main(self, config):
        self._service_register(ZeroFWService, master=True)
        service_id = ZeroFWService.__dict__.get('name')
        container = ServiceContainer(ZeroFWService, config={"AMQP_URI": config})
        return container, service_id

    def _get_container_main_config(self, config):
        self._service_register(ZeroFWConfig)
        service_id = ZeroFWConfig.__dict__.get('name')
        container = ServiceContainer(ZeroFWConfig, config={"AMQP_URI": config})
        return container, service_id
