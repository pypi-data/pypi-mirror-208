"""
@time 2023-4-2
@auther YanPing
"""
from ._network import _Network


class Network(_Network):

    def _get_ipaddr(self):
        """
        Obtain intranet IP
        :return:
        """
        return super()._get_ipaddr()

    def _post(self, url, headers, data):
        """
        Send a post request
        :param url: request url
        :param headers: request headers
        :param data: request data，type json
        :return:
        """
        return super()._post(url, headers, data)
