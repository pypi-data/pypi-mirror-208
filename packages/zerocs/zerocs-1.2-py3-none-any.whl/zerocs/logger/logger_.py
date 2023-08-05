"""
@time 2023-4-2
@auther YanPing
"""
from ._logger import _Logger


class Logger(_Logger):

    def _logger(self, snowflake_id, log_path, filename):
        """
        logger
        :param snowflake_id: snowflake id
        :param log_path: log file path
        :param filename: log file name
        :return:
        """
        return super()._logger(snowflake_id, log_path, filename)
