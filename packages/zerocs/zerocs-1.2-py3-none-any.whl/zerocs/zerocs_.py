"""

@time 2023-4-1
@auther YanPing

Before using the zerocs framework, please carefully read and fully understand this statement.
You can choose not to use the zerocs framework, but once you use the zerocs framework,
Your usage behavior is deemed to be recognition and acceptance of the entire content of this statement.

+ You promise to use the zerocs framework in a legal and reasonable manner,
Do not use the zerocs board framework to engage in any illegal or malicious behavior that infringes
on the legitimate interests of others,
We will not apply the zerocs framework to any platform that violates Chinese laws and regulations.

+ Any accident, negligence, contract damage, defamation
This project does not assume any legal responsibility for copyright or intellectual property
infringement and any losses caused (including but not limited to direct, indirect, incidental or derivative losses).

+ The user clearly and agrees to all the contents listed in the terms of this statement,
The potential risks and related consequences of using the zerocs framework will be entirely borne by the user,
and this project will not bear any legal responsibility.

+ After reading this disclaimer, any unit or individual should obtain the MIT Open Source License
Conduct legitimate publishing, dissemination, and use of the zerocs framework within the permitted scope,
If the breach of this disclaimer clause or the violation of laws and regulations results in legal
liability (including but not limited to civil compensation and criminal liability),
the defaulter shall bear the responsibility on their own.

+ The author owns intellectual property rights (including but not limited to trademark rights, patents, Copyrights,
trade secrets, etc.) of zerocs framework, and the above products are protected by relevant laws and regulations

+ No entity or individual shall apply for intellectual property rights related to
the zerocs Framework itself without the written authorization of the Author.

+ If any part of this statement is deemed invalid or unenforceable,
the remaining parts shall remain in full force and effect.
An unenforceable partial declaration does not constitute a waiver of our
right to enforce the declaration.

+ This project has the right to make unilateral changes to the terms and attachments of this statement at any time,
and publish them through message push, webpage announcement, and other means. Once published,
it will automatically take effect without the need for separate notice;
If you continue to use this statement after the announcement of changes,
it means that you have fully read, understood, and accepted the revised statement.
"""

import os
import hashlib
from nameko.standalone.rpc import ClusterRpcProxy

from zerocs.base import Base, Function
from zerocs.fork import *
from zerocs.script import *
from zerocs.sqlite import *
from zerocs.logger import *
from zerocs.network import *
from zerocs.rabbitmq import *
from zerocs.snowflakeId import *


class MetaClass(Base, Fork, Queue, Logger, RabbitMq, Network, SnowflakeId, SqlIte, Function):
    RABBITMQ_STR = None
    RABBITMQ_PORT = None
    ZERO_FW_DB_FILE = None
    RABBITMQ_CONFIG = None

    RABBITMQ_CONFIG_URL = None
    ZERO_FW_LOGS_PATH = None
    ZERO_FW_FILE_PATH = None
    ZERO_FW_P_VERSION = None
    ZERO_PROJECT_PATH = None
    ZERO_FW_SERVICE_PATH = None
    ZERO_FW_RABBITMQ_CONFIG = None

    def _getenv(self):
        self.RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')
        self.RABBITMQ_CONFIG = os.getenv('RABBITMQ_CONFIG')
        self.RABBITMQ_CONFIG_URL = os.getenv('RABBITMQ_CONFIG_URL')
        self.ZERO_FW_LOGS_PATH = os.getenv('ZERO_FW_LOGS_PATH')
        self.ZERO_FW_FILE_PATH = os.getenv('ZERO_FW_FILE_PATH')
        self.ZERO_PROJECT_PATH = os.getenv('ZERO_PROJECT_PATH')
        self.ZERO_FW_SERVICE_PATH = os.getenv('ZERO_FW_SERVICE_PATH')
        self.ZERO_FW_DB_FILE = os.getenv('ZERO_FW_DB_FILE')
        self.ZERO_FW_NODE_MASTER = os.getenv('ZERO_FW_NODE_MASTER')

        self.rabbitmq_init_()
        if self.ZERO_FW_NODE_MASTER == 'True':
            self._sqlite_init()

    def _sqlite_init(self):
        db_file = os.path.join(self.ZERO_PROJECT_PATH, self.ZERO_FW_DB_FILE)
        self._connect_db(db_file)
        self._sqlite_create_table_system()
        self._sqlite_create_table_task_id()

    def _add_service(self, service, service_id, queue_pid, rpc_pid):
        """
        add service
        :param service:
        :param service_id:
        :param queue_pid:
        :param rpc_pid:
        :return:
        """
        if self.ZERO_FW_NODE_MASTER == 'True':
            self._sqlite_insert_service(service_name=service, max_work='1', node_ip=self.get_ipaddr(),
                                        service_id=service_id, service_status='init',
                                        queue_id=queue_pid, rpc_id=rpc_pid)
        else:
            self.rpc_obj.zerocs_service.set_service(service, '1', self.get_ipaddr(),
                                                    service_id, 'init', queue_pid, rpc_pid)

    def _get_max_work(self, node_ip, service_name):
        """
        Obtain the maximum number of work served by the specified node
        :param node_ip:
        :param service_name:
        :return:
        """
        service_info = self._sqlite_get_service_by_ip_name(node_ip, service_name)
        service_id = service_info[0]['service_id']
        service_obj = getattr(self.rpc_obj, service_id)
        return service_obj.get_max_work_num()

    def _update_max_work(self, node_ip, service_name, work_num):
        """
        Update the maximum number of work served by the specified node
        :param node_ip:
        :param service_name:
        :param work_num:
        :return:
        """
        service_info = self._sqlite_get_service_by_ip_name(node_ip, service_name)
        service_id = service_info[0]['service_id']
        service_obj = getattr(self.rpc_obj, service_id)
        self._sqlite_update_service_max_work(node_ip, service_name, work_num)
        return service_obj.update_max_work_num(work_num)

    def _get_service_info(self, node_ip, service_name):
        """
        Get service info
        :param node_ip:
        :param service_name:
        :return:
        """
        service_info = self._sqlite_get_service_by_ip_name(node_ip, service_name)
        config_id = hashlib.md5(f"{node_ip}_zerocs_config".encode('utf-8')).hexdigest()
        queue_pid = service_info[0]['queue_pid']
        rpc_pid = service_info[0]['rpc_pid']
        return config_id, queue_pid, rpc_pid

    def _stop_service(self, node_ip, service_name):
        """
        stop service
        :param node_ip:
        :param service_name:
        :return:
        """
        config_id, queue_pid, rpc_pid = self._get_service_info(node_ip, service_name)
        service_obj = getattr(self.rpc_obj, config_id)
        return service_obj.stop_service(node_ip, service_name, rpc_pid, queue_pid)

    def _restart_service(self, node_ip, service_name):
        """
        restart service
        :param node_ip:
        :param service_name:
        :return:
        """
        config_id, queue_pid, rpc_pid = self._get_service_info(node_ip, service_name)
        service_obj = getattr(self.rpc_obj, config_id)
        return service_obj.restart_service(node_ip, service_name, rpc_pid, queue_pid)

    def _stop_task(self, service_name, task_id):
        """
        Stop the task,
        :param service_name: Task type, service name
        :param task_id:
        :return:
        """
        self._sqlite_insert_task_id(service_name, task_id)

    def _get_all_stop_task(self):
        """
        Get ALL Stop Task
        :return:
        """
        return self._sqlite_get_all_task_id()

    def _service_init(self):
        """
        Service initialization
        :return:
        """
        self.rpc_obj = ClusterRpcProxy({'AMQP_URI': self.ZERO_FW_RABBITMQ_CONFIG}).start()
        default_service = ['zerocs_service', 'zerocs_config']

        if self.ZERO_FW_NODE_MASTER == 'True':
            container, service_id = self._get_container_main(self.ZERO_FW_RABBITMQ_CONFIG)
            self._container_fork(container)
            self._add_service('zerocs_service', service_id, '--', '--')

        container, service_id = self._get_container_main_config(self.ZERO_FW_RABBITMQ_CONFIG)
        self._container_fork(container)
        self._add_service('zerocs_config', service_id, '--', '--')

        for service in os.listdir(self.ZERO_FW_SERVICE_PATH):
            if service in default_service:
                raise f'Service name conflicts with default service， default: {default_service}'

            os.environ[f'{service}_MAX_WORK'] = "1"
            queue_pid = self._work_fork(service, self.RABBITMQ_STR)
            self.logger(service).error(f'work {service} start, queue_pid: {queue_pid}')

            container, service_id = self._get_container(service, self.ZERO_FW_RABBITMQ_CONFIG)
            rpc_pid = self._container_fork(container)
            self.logger(service).error(f'queue {service} start, rpc_pid: {rpc_pid}')
            self._add_service(service, service_id, queue_pid, rpc_pid)

    def _get_all_service(self):
        """
        Get All Service
        :return:
        """
        all_service = self._sqlite_get_all_service()
        _service_list = []
        for s in all_service:
            service_name = s['service_name']
            if service_name not in ['zerocs_service', 'zerocs_config']:
                _service_list.append(s)
        return _service_list

    def get_snowflake_id(self):
        """
        Obtain IDs, with a maximum of 4000 retrieved per millisecond
        :return:
        """
        return self._get_snowflake_id(datacenter_id=0, worker_id=0, did_wid=-1)

    def logger(self, log_name):
        """
        log_path = os.path.join(ZERO_PROJECT_PATH, ZERO_FW_LOGS_PATH)  \n \n
        Create a log file {log_name} in the log_path directory and write it to the logs
        :param log_name: log file name
        :return:
        """
        log_path = os.path.join(self.ZERO_PROJECT_PATH, self.ZERO_FW_LOGS_PATH)
        return self._logger(self.get_snowflake_id(), log_path, log_name)

    def rabbitmq_init_(self):
        """
        Get RabbitMQ Channel
        """
        if self.RABBITMQ_CONFIG is not None and self.RABBITMQ_CONFIG != '':
            self.ZERO_FW_RABBITMQ_CONFIG = self.RABBITMQ_CONFIG
        else:
            res = self._post(self.RABBITMQ_CONFIG_URL, headers=None, data=None)
            self.ZERO_FW_RABBITMQ_CONFIG = res.json()['RM_CONFIG']['AMQP_URI']

        os.environ['ZERO_FW_RABBITMQ_CONFIG'] = self.ZERO_FW_RABBITMQ_CONFIG
        self.RABBITMQ_STR = self.ZERO_FW_RABBITMQ_CONFIG.split('//')[1].split(':')

        self._rabbitmq_init(self.RABBITMQ_STR, self.RABBITMQ_PORT)

    def send_message(self, queue, message):
        """
        Send data to Message Queuing
        :param queue: queue name
        :param message: data
        :return:
        """
        self._send_message(queue, message)

    def get_message(self, queue, callback):
        """
        Obtain message queue data and use the incoming callback function to process the data
        :param queue: queue name
        :param callback: Callback function
        :return:
        """
        self._get_message(queue, callback)

    def get_ipaddr(self):
        """
        Obtain intranet IP
        :return:
        """
        return self._get_ipaddr()
