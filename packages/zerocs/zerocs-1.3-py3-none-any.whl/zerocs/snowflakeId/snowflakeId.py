"""
@time 2023-4-8
@auther YanPing
"""
from ._snowflakeId import _SnowflakeId


class SnowflakeId(_SnowflakeId):

    def _get_snowflake_id(self, datacenter_id, worker_id, did_wid):
        """
        Get Snowflake Id
        :param datacenter_id: data center id, default 0
        :param worker_id: work id, default 0
        :param did_wid: did wid, default -1
        :return:
        """
        return super()._get_snowflake_id(datacenter_id, worker_id, did_wid)
