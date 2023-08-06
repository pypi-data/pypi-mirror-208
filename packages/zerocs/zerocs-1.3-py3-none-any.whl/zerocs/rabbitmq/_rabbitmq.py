"""
@time 2023-4-2
@auther YanPing
"""
import json

import pika
from zerocs.mate import _Mate


class _RabbitMq(_Mate):

    def _rabbitmq_init(self, rabbit_mq, rabbit_port):
        host = rabbit_mq[1].split('@')[1]
        user = rabbit_mq[0]
        passwd = rabbit_mq[1].split('@')[0]
        self._get_mq_channel(host, user, passwd, rabbit_port)

    def _get_mq_channel(self, host, user, passwd, port):
        credentials = pika.PlainCredentials(user, passwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host, port=port, virtual_host='/', credentials=credentials, heartbeat=0))
        self.mq_channel = connection.channel()

    def _create_queue(self, queue):
        try:
            self.mq_channel.queue_declare(queue=queue)
        except Exception as e:
            raise e

    def _send_message(self, queue, message):
        # self._create_queue(queue=queue)
        if type(message) is not str:
            message = json.dumps(message)
        self.mq_channel.basic_publish(exchange='', routing_key=queue, body=message)

    def _get_message(self, queue, callback):
        self._create_queue(queue=queue)
        self.mq_channel.basic_consume(on_message_callback=callback, queue=queue)
        self.mq_channel.start_consuming()
