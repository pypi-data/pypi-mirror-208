"""
@time 2023-4-2
@auther YanPing
"""
from ._rabbitmq import _RabbitMq


class RabbitMq(_RabbitMq):

    def _rabbitmq_init(self, config=None, rabbit_port=5672):
        """
        Get RabbitMQ Channel
        """
        super()._rabbitmq_init(config, rabbit_port)

    def _get_mq_channel(self, host, user, passwd, port):
        """
        Get RabbitMQ Channel
        :param host: rabbit host
        :param user: rabbit user
        :param passwd: rabbit passwd
        :param port: rabbit port
        :return:
        """
        super()._get_mq_channel(host, user, passwd, port)

    def _create_queue(self, queue):
        """
        Create Queue
        :param queue: queue name
        :return:
        """
        super()._create_queue(queue)

    def _send_message(self, queue, message):
        """
        Send data to Message Queuing
        :param queue: queue name
        :param message: data
        :return:
        """
        super()._send_message(queue, message)

    def _get_message(self, queue, callback):
        """
        Obtain message queue data and use the incoming callback function to process the data
        :param queue: queue name
        :param callback: Callback function
        :return:
        """
        super()._get_message(queue, callback)
