import pika


# 链接到rabbitmq服务器
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
# 创建频道，声明消息队列
channel = connection.channel()

# 和生产者声明同一个队列，如果一方挂掉，不会丢失数据
channel.queue_declare(queue='zhuozi')

# 定义接受消息的回调函数
def callback(channel, method, properties, body):
    print(body)
# 告诉RabbitMQ使用callback来接收信息
channel.basic_consume(on_message_callback=callback, queue='zhuozi', auto_ack=True)
# 开始接收信息
channel.start_consuming()