"""
@time 2023-4-2
@auther YanPing
"""

import os
import hashlib

from nameko.rpc import rpc
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.containers import ServiceContainer

from zerocs.network import Network
from zerocs.fork import Fork
from zerocs.sqlite import SqlIte
from zerocs.logger import Logger
from zerocs.snowflakeId import SnowflakeId
from zerocs.mate import _Mate

from .base_ import Base
from .function_ import Function


class _ZeroFWService(SqlIte, Base, Logger, SnowflakeId):
    service_name = 'zerocs_service'

    @staticmethod
    def sqlite_init():
        _path = os.getenv('ZERO_PROJECT_PATH')
        _file = os.getenv('ZERO_FW_DB_FILE')
        db_file = os.path.join(_path, _file)
        SqlIte()._connect_db(db_file)

    def _log(self, msg):
        _path = os.getenv('ZERO_PROJECT_PATH')
        _file = os.getenv('ZERO_FW_LOGS_PATH')
        log_path = os.path.join(_path, _file)
        logger_ = self._logger(self._get_snowflake_id(datacenter_id=0, worker_id=0, did_wid=-1),
                               log_path, self.service_name)
        logger_.error(msg)

    @rpc
    def zero_status(self):
        return {"code": 0, "msg": "zero status start"}

    @rpc
    def set_service(self, service_name, max_work, node_ip, service_id, service_status, queue_id, rpc_id):
        self.sqlite_init()
        self._sqlite_insert_service(service_name, max_work, node_ip, service_id, service_status, queue_id, rpc_id)

        self._log(f"set_service: {service_name, max_work, node_ip, service_id, service_status, queue_id, rpc_id}")
        return {"code": 0, "msg": "register service success"}

    @rpc
    def update_service_max_work(self, node_ip, service_name, max_work):
        self.sqlite_init()
        self._sqlite_update_service_max_work(node_ip=node_ip, service_name=service_name, max_work=max_work)

        self._log(f"update_service_max_work: {node_ip, service_name, max_work}")
        return {"code": 0, "msg": "update service max work success"}

    @rpc
    def update_service_rpc_id(self, node_ip, service_name, rpc_id):
        self.sqlite_init()
        self._sqlite_update_service_rpc_id(node_ip=node_ip, service_name=service_name, rpc_id=rpc_id)

        self._log(f"update_service_rpc_id: {node_ip, service_name, rpc_id}")
        return {"code": 0, "msg": "update service rpc_id success"}

    @rpc
    def update_service_queue_id(self, node_ip, service_name, queue_id):
        self.sqlite_init()
        self._sqlite_update_service_queue_id(node_ip=node_ip, service_name=service_name, queue_id=queue_id)

        self._log(f"update_service_queue_id: {node_ip, service_name, queue_id}")
        return {"code": 0, "msg": "update service queue_id success"}

    @rpc
    def update_service_status(self, node_ip, service_name, status):
        self.sqlite_init()
        self._sqlite_update_service_status(node_ip=node_ip, service_name=service_name, service_status=status)

        self._log(f"update_service_status: {node_ip, service_name, status}")
        return {"code": 0, "msg": "update service status success"}

    @rpc
    def get_task_id(self, service_name, task_id):
        self.sqlite_init()
        return self._sqlite_get_task_id(service_name, task_id)


class _DefaultFunc(Base, Function, Network):

    @rpc
    def update_max_work_num(self, work_num):
        service_name = self.__class__.__dict__['service_name']
        os.environ[f'{service_name}_MAX_WORK'] = f'{work_num}'
        return {"code": 0, "msg": "update max work success"}

    @rpc
    def get_max_work_num(self):
        service_name = self.__class__.__dict__['service_name']
        max_work = os.getenv(f'{service_name}_MAX_WORK')
        return int(max_work) if max_work is not None else 1

    def __init__(self, build):
        self.build = build

    def add_default_func(self, func, master):
        ipaddr = self._get_ipaddr()
        service_name = func.service_name
        name = hashlib.md5(f"{ipaddr}_{service_name}".encode('utf-8')).hexdigest()

        self._set_str('service_name', service_name)
        if master:
            self._set_cls_function(func, 'name', service_name)
        else:
            self._set_cls_function(func, 'name', name)

        self._set_cls_function(func, 'update_max_work_num', _DefaultFunc.update_max_work_num)
        self._set_cls_function(func, 'get_max_work_num', _DefaultFunc.get_max_work_num)


class _DefaultConfig(_Mate):

    def _default_build(self):
        return _DefaultFunc(self)


class _ServiceRegister(_DefaultConfig):

    def _service_register(self, cls, master):
        s = _DefaultConfig()
        b = s._default_build()
        b.add_default_func(cls, master)


class _ZeroFWConfig(Base, Function, Fork, _ServiceRegister, Logger, SnowflakeId):
    service_name = 'zerocs_config'

    def _log(self, msg):
        _path = os.getenv('ZERO_PROJECT_PATH')
        _file = os.getenv('ZERO_FW_LOGS_PATH')
        log_path = os.path.join(_path, _file)
        logger_ = self._logger(self._get_snowflake_id(datacenter_id=0, worker_id=0, did_wid=-1),
                               log_path, self.service_name)
        logger_.error(msg)

    @staticmethod
    def rpc_proxy():
        _config = os.getenv('ZERO_FW_RABBITMQ_CONFIG')
        rpc_obj = ClusterRpcProxy({'AMQP_URI': _config}).start()
        return rpc_obj.zerocs_service

    @rpc
    def zero_status(self):
        return {"code": 0, "msg": "zero status start"}

    @rpc
    def stop_service(self, node_ip, service_name, rpc_pid, queue_pid):
        os.system(f'kill -9 {rpc_pid}')
        os.system(f'kill -9 {queue_pid}')
        self.rpc_proxy().update_service_status(node_ip, service_name, 'stop')
        return {"code": 0, "msg": "stop service success"}

    @rpc
    def restart_service(self, node_ip, service_name, rpc_pid, queue_pid):
        try:
            os.system(f'kill -9 {rpc_pid}')
            os.system(f'kill -9 {queue_pid}')
        except IOError:
            self._log('kill error')
        _config = os.getenv('ZERO_FW_RABBITMQ_CONFIG')
        _str = _config.split('//')[1].split(':')

        # container, service_id = self._get_container(service_name, _config)
        # rpc_pid = self._container_fork(container)

        service_path = os.getenv('ZERO_FW_SERVICE_PATH')
        module = __import__(f"{service_path}.{service_name}.{service_name}",
                            globals=globals(), locals=locals(), fromlist=['RpcFunction'])
        cls = module.RpcFunction

        self._service_register(cls, master=False)

        container = ServiceContainer(cls, config={"AMQP_URI": _config})
        rpc_pid = self._container_fork(container)
        self._log(f'service restart, new pid : {rpc_pid}')

        os.environ[f'{service_name}_max_work'] = '1'
        queue_pid = self._work_fork(service_name, _str)

        self.rpc_proxy().update_service_status(node_ip, service_name, 'restart')
        self.rpc_proxy().update_service_max_work(node_ip, service_name, 1)
        self.rpc_proxy().update_service_rpc_id(node_ip, service_name, rpc_pid)
        self.rpc_proxy().update_service_queue_id(node_ip, service_name, queue_pid)
        return {"code": 0, "msg": "restart service success"}
