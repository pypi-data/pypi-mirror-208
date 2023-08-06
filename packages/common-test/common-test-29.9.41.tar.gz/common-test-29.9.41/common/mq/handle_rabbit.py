import json
import sysconfig
import yaml
import os
import pika



class RabbitmqUtil:
    """Rabbitmq工具类"""
    connection = None
    channel = None

    def __init__(self, host, vhost, username, password, port=5672):
        try:
            credential = pika.PlainCredentials(username, password)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host, port, vhost, credential, heartbeat=0))
            self.channel = self.connection.channel()
        except():
            print("rabbitmq init error, please check the config")

    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
        else:
            print("connection already disconnected")

    def bind_queue_exchange(self, queue, exchange, routing_key):
        """绑定queue和exchange"""
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

    def new_queue(self, queue):
        """声明queue，如不存在，则创建"""
        self.channel.queue_declare(queue=queue, durable=True, arguments={'x-message-ttl': 259200000})

    def del_queue(self, queue):
        """Delete the queue"""
        self.channel.queue_delete(queue)

    def new_exchange(self, exchange):
        """声明exchange，如不存在，则创建"""
        self.channel.exchange_declare(exchange=exchange, durable=True, exchange_type='topic')

    def del_exchange(self, exchange):
        """Delete the exchange"""
        self.channel.exchange_delete(exchange=exchange)

    def callback(self, body):
        """接收处理消息的回调函数"""
        super()
        print(str(body).replace('b', '').replace('\'', ''))

    def public_msg(self, exchange, routing_key, json):
        """发布消息"""
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json)

    def consume_msg(self, queue):
        """订阅消息"""
        self.channel.basic_consume(queue, self.callback, True)
        self.channel.start_consuming()

