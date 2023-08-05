"""
@time 2023-4-2
@auther YanPing
"""
from ._sqlite import _SqlIte


class SqlIte(_SqlIte):

    def _connect_db(self, db_file):
        """
        open db file
        :param db_file:
        :return:
        """
        super()._connect_db(db_file)

    def _sqlite_create_table_system(self):
        """
        create system info table
        :return:
        """
        super()._sqlite_create_table_system()

    def _sqlite_create_table_task_id(self):
        """
        create task ids table
        :return:
        """
        super()._sqlite_create_table_task_id()

    def _sqlite_get_all_service(self):
        """
        get all service
        :return:
        """
        return super()._sqlite_get_all_service()

    def _sqlite_get_service_by_ip_name(self, node_ip, service_name):
        """
        Obtain services by name and IP query
        :param node_ip: node ip / service ip
        :param service_name: service name
        :return:
        """
        return super()._sqlite_get_service_by_ip_name(node_ip, service_name)

    def _sqlite_insert_service(self, service_name, max_work, node_ip, service_id, service_status, queue_id, rpc_id):
        """
        Add service info
        :param service_name: service name
        :param max_work: max work
        :param node_ip: node ip
        :param service_id: service id
        :param service_status: service status
        :param queue_id: task queue proces id
        :param rpc_id: nameko service rpc function proces id
        :return:
        """
        super()._sqlite_insert_service(service_name, max_work, node_ip, service_id, service_status, queue_id, rpc_id)

    def _sqlite_update_service_max_work(self, node_ip, service_name, max_work):
        """
        update service max work
        :param node_ip:
        :param service_name:
        :param max_work:
        :return:
        """
        super()._sqlite_update_service_max_work(node_ip, service_name, max_work)

    def _sqlite_update_service_status(self, node_ip, service_name, service_status):
        """
        update service status
        :param node_ip:
        :param service_name:
        :param service_status:
        :return:
        """
        super()._sqlite_update_service_status(node_ip, service_name, service_status)

    def _sqlite_update_service_queue_id(self, node_ip, service_name, queue_id):
        """
        update service queue proces id
        :param node_ip:
        :param service_name:
        :param queue_id:
        :return:
        """
        super()._sqlite_update_service_queue_id(node_ip, service_name, queue_id)

    def _sqlite_update_service_rpc_id(self, node_ip, service_name, rpc_id):
        """
        update service proces id
        :param node_ip:
        :param service_name:
        :param rpc_id:
        :return:
        """
        super()._sqlite_update_service_rpc_id(node_ip, service_name, rpc_id)

    def _sqlite_get_task_id(self, service_name, task_id):
        """
        get Task ID stopped
        :param service_name:
        :param task_id: task id
        :return:
        """
        return super()._sqlite_get_task_id(service_name, task_id)

    def _sqlite_insert_task_id(self, service_name, task_id):
        """
        insert Task ID stopped
        :param service_name:
        :param task_id:
        :return:
        """
        super()._sqlite_insert_task_id(service_name, task_id)

    def _sqlite_get_all_task_id(self):
        """
        Get All stop task
        :return:
        """
        return super()._sqlite_get_all_task_id()
