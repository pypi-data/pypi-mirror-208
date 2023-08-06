"""
@time 2023-4-2
@auther YanPing
"""
import socket

import requests

from zerocs.mate import _Mate


class _Network(_Mate):

    def _get_ipaddr(self):
        socket_tools = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_tools.connect(("8.8.8.8", 80))
        return socket_tools.getsockname()[0]

    def _post(self, url, headers, data):
        return requests.post(url=url, headers=headers, data=data)
