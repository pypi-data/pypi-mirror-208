"""
@time 2023-4-1
@auther YnaPing

"""


class _Mate:

    def _set(self, attr_name, value):
        """
        Set attr for the current class
        :param attr_name: attr name
        :param value: attr value
        :return:
        """

    def _get_dict(self):
        """
        get __dict__ for the current class
        :return:
        """

    def _get_class_dict(self):
        """
        get __class__.__dict__ for the current class
        :return:
        """

    def _call_sub_function(self, name):
        """
        Calling a sub function method
        :param name: sub function name
        :return:
        """

    def _get_attr(self, attr_name):
        """
        get attr for the current class.__dict__
        :param attr_name:
        :return:
        """

    def _set_str(self, attr_name, value):
        """
        Set attr for the current class, type str
        :param attr_name: attr name
        :param value: attr value
        :return:
        """

    def _set_int(self, attr_name, value):
        """
        Set attr for the current class, type int
        :param attr_name: attr name
        :param value: attr value
        :return:
        """

    def _set_list(self, attr_name, value):
        """
        Set attr for the current class, type list
        :param attr_name: attr name
        :param value: attr value
        :return:
        """

    def _set_dict(self, attr_name, value):
        """
        Set attr for the current class, type dict
        :param attr_name: attr name
        :param value: attr value
        :return:
        """

    def _list_append(self, attr_name, value):
        """
        Add a value to the specified list
        :param attr_name: attr name
        :param value: attr value
        :return:
        """

    def _get_timestamp_millimeter(self):
        """
        Get millimeter timestamp
        :return:
        """

    def _get_timestamp_next_second(self, last_timestamp):
        """
        Get next second timestamp
        :param last_timestamp: last timestamp
        :return:
        """

    def _set_function(self, func_name, value):
        """
         Set function for the current class, type dict
        :param func_name: function name
        :param value: function obj
        :return:
        """

    def _set_cls_function(self, cls, func_name, value):
        """
        Add a method to the specified class
        :param cls: cls obj
        :param func_name: function name
        :param value: function obj
        :return:
        """

    def _get_ipaddr(self):
        """
        Obtain intranet IP
        :return:
        """

    def _post(self, url, headers, data):
        """
        Send a post request
        :param url: request url
        :param headers: request headers
        :param data: request data，type json
        :return:
        """

    def _get_sequence(self, sequence, last_timestamp, sequence_mask):
        """
        Get Serial Number
        :param sequence: sequence
        :param last_timestamp: last timestamp
        :param sequence_mask: sequence mask
        :return:
        """

    def _get_snowflake_id(self, datacenter_id, worker_id, did_wid):
        """
        Get Snowflake Id
        :param datacenter_id: data center id, default 0
        :param worker_id: work id, default 0
        :param did_wid: did wid, default -1
        :return:
        """

    def _logger(self, snowflake_id, log_path, filename):
        """
        logger
        :param snowflake_id: snowflake id
        :param log_path: log file path
        :param filename: log file name
        :return:
        """

    def _service_register(self, cls, master):
        """
        The service class object to register
        :param cls: class
        :return:
        """

    def _send_message(self, queue, message):
        """
        Send data to Message Queuing
        :param queue: queue name
        :param message: data
        :return:
        """

    def _get_message(self, queue, callback):
        """
        Obtain message queue data and use the incoming callback function to process the data
        :param queue: queue name
        :param callback: Callback function
        :return:
        """

    def _get_func_module(self, service_name):
        """
        Obtain Service Objects
        :param service_name: service name
        :return:
        """

    def _get_container(self, service_name, config):
        """
        Get Rpc Container
        :param service_name:
        :param config:
        :return:
        """

    def _container_start(self, container):
        """
        container start
        :param container:  container obj
        :return:
        """

    def _connect_db(self, db_file):
        """
        open db file
        :param db_file:
        :return:
        """

    def _sqlite_create_table_system(self):
        """
        create system info table
        :return:
        """

    def _sqlite_create_table_task_id(self):
        """
        create task ids table
        :return:
        """

    def _sqlite_get_all_service(self):
        """
        get all service
        :return:
        """

    def _sqlite_get_service_by_ip_name(self, node_ip, service_name):
        """
        Obtain services by name and IP query
        :param node_ip: node ip / service ip
        :param service_name: service name
        :return:
        """

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

    def _sqlite_update_service_max_work(self, node_ip, service_name, max_work):
        """
        update service max work
        :param node_ip:
        :param service_name:
        :param max_work:
        :return:
        """

    def _sqlite_update_service_status(self, node_ip, service_name, service_status):
        """
        update service status
        :param node_ip:
        :param service_name:
        :param service_status:
        :return:
        """

    def _sqlite_update_service_queue_id(self, node_ip, service_name, queue_id):
        """
        update service queue proces id
        :param node_ip:
        :param service_name:
        :param queue_id:
        :return:
        """

    def _sqlite_update_service_rpc_id(self, node_ip, service_name, rpc_id):
        """
        update service proces id
        :param node_ip:
        :param service_name:
        :param rpc_id:
        :return:
        """

    def _sqlite_get_task_id(self, service_name, task_id):
        """
        get Task ID stopped
        :param service_name:
        :param task_id: task id
        :return:
        """

    def _sqlite_insert_task_id(self, service_name, task_id):
        """
        insert Task ID stopped
        :param service_name:
        :param task_id:
        :return:
        """

    def _sqlite_get_all_task_id(self):
        """
        Get All stop task
        :return:
        """