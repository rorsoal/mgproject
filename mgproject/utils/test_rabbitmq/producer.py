import pika


# 链接到RabbitMQ服务器
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))

#创建频道
channel = connection.channel()

# 声明消息队列
channel.queue_declare(queue='zhuozi')

# routing_key是队列名 body是要插入的内容
channel.basic_publish(exchange='', routing_key='zhuozi',body=b'Hello RabbitMQ!')
print("开始向 'zhuozi' 队列中发布消息 '汉堡做好啦!'")


# 关闭链接
connection.close()