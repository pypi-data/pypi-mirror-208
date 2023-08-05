"""
@time 2023-4-8
@auther YanPing
"""
import os
import sqlite3

from zerocs.mate import _Mate


class _SqlIte(_Mate):

    def _connect_db(self, db_file):
        self._conn = sqlite3.connect(db_file)
        self._cursor = self._conn.cursor()

    def _execute(self, _sql):
        ZERO_PROJECT_PATH = os.getenv('ZERO_PROJECT_PATH')
        ZERO_FW_DB_FILE = os.getenv('ZERO_FW_DB_FILE')
        db_file = os.path.join(ZERO_PROJECT_PATH, ZERO_FW_DB_FILE)
        self._connect_db(db_file)
        return self._cursor.execute(_sql)

    def _is_table(self, table_name):
        _sql = f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        cursor = self._execute(_sql)
        for i in cursor:
            if i[0] > 0:
                return True
            else:
                return False

    def _sqlite_create_table_system(self):
        _sql = f"""CREATE TABLE SYSTEMINFO(
        SERVICE_NAME TEXT NOT NULL,
        MAX_WORK TEXT NOT NULL,
        NODE_IP TEXT NOT NULL,
        SERVICE_ID TEXT NOT NULL,
        SERVICE_STATUS TEXT NOT NULL,
        QUEUE_PID TEXT NOT NULL,
        RPC_PID TEXT NOT NULL
        );"""

        if self._is_table('SYSTEMINFO') is False:
            self._execute(_sql)
            self._conn.commit()

    def _sqlite_create_table_task_id(self):
        _sql = f"""CREATE TABLE TASKID(
        SERVICE_NAME TEXT NOT NULL,
        TASK_ID TEXT NOT NULL
        );"""
        if self._is_table('TASKID') is False:
            self._execute(_sql)
            self._conn.commit()

    def _sqlite_get_all_service(self):
        _sql = f"""SELECT * FROM SYSTEMINFO"""
        cursor = self._execute(_sql)
        service_list = []
        for i in list(cursor):
            s = {
                "service_name": i[0],
                "max_work": i[1],
                "node_ip": i[2],
                "service_id": i[3],
                "status": i[4],
                "queue_pid": i[5],
                "rpc_pid": i[6]
            }
            service_list.append(s)
        return service_list

    def _sqlite_get_service_by_ip_name(self, node_ip, service_name):
        _sql = f"""SELECT * FROM SYSTEMINFO WHERE \
        SERVICE_NAME="{service_name}" AND NODE_IP="{node_ip}"; """
        cursor = self._execute(_sql)

        service_list = []
        for i in list(cursor):
            s = {
                "service_name": i[0],
                "max_work": i[1],
                "node_ip": i[2],
                "service_id": i[3],
                "status": i[4],
                "queue_pid": i[5],
                "rpc_pid": i[6]
            }
            service_list.append(s)
        return service_list

    def _sqlite_insert_service(self, service_name, max_work, node_ip, service_id, service_status, queue_id, rpc_id):
        if len(self._sqlite_get_service_by_ip_name(node_ip, service_name)) < 1:
            _sql = f"""INSERT INTO SYSTEMINFO (SERVICE_NAME,MAX_WORK,NODE_IP,SERVICE_ID,
            SERVICE_STATUS,QUEUE_PID,RPC_PID) VALUES ("{service_name}", "{max_work}", "{node_ip}", "{service_id}",
            "{service_status}", "{queue_id}", "{rpc_id}")"""
        else:
            _sql = f"""UPDATE SYSTEMINFO SET SERVICE_NAME="{service_name}",MAX_WORK="{max_work}",NODE_IP="{node_ip}",\
            SERVICE_ID="{service_id}",SERVICE_STATUS="{service_status}",QUEUE_PID="{queue_id}",RPC_PID="{rpc_id}" \
            WHERE SERVICE_NAME="{service_name}" AND NODE_IP="{node_ip}"; """

        self._execute(_sql)
        self._conn.commit()

    def _sqlite_update_service_max_work(self, node_ip, service_name, max_work):
        _sql = f"""UPDATE SYSTEMINFO SET MAX_WORK="{max_work}" WHERE \
        SERVICE_NAME="{service_name}" AND NODE_IP="{node_ip}"; """
        self._execute(_sql)
        self._conn.commit()

    def _sqlite_update_service_status(self, node_ip, service_name, service_status):
        _sql = f"""UPDATE SYSTEMINFO SET SERVICE_STATUS="{service_status}" WHERE \
        SERVICE_NAME="{service_name}" AND NODE_IP="{node_ip}"; """
        self._execute(_sql)
        self._conn.commit()

    def _sqlite_update_service_queue_id(self, node_ip, service_name, queue_id):
        _sql = f"""UPDATE SYSTEMINFO SET QUEUE_PID="{queue_id}" WHERE \
        SERVICE_NAME="{service_name}" AND NODE_IP="{node_ip}"; """
        self._execute(_sql)
        self._conn.commit()

    def _sqlite_update_service_rpc_id(self, node_ip, service_name, rpc_id):
        _sql = f"""UPDATE SYSTEMINFO SET RPC_PID="{rpc_id}" WHERE \
        SERVICE_NAME="{service_name}" AND NODE_IP="{node_ip}"; """
        self._execute(_sql)
        self._conn.commit()

    def _sqlite_get_task_id(self, service_name, task_id):
        _sql = f"""SELECT * FROM TASKID WHERE SERVICE_NAME="{service_name}" AND TASK_ID="{task_id}"; """
        cursor = self._execute(_sql)

        task_ids = []
        for i in list(cursor):
            task_ids.append(i[1])
        return task_ids

    def _sqlite_insert_task_id(self, service_name, task_id):
        if len(self._sqlite_get_task_id(service_name, task_id)) < 1:
            _sql = f"""INSERT INTO TASKID (SERVICE_NAME,TASK_ID) VALUES ("{service_name}", "{task_id}")"""
        else:
            _sql = f""""""

        self._execute(_sql)
        self._conn.commit()

    def _sqlite_get_all_task_id(self):
        _sql = f"""SELECT * FROM TASKID;"""
        cursor = self._execute(_sql)

        task_ids = []
        for i in list(cursor):
            task_ids.append(i[1])
        return task_ids
