# 2022.4.28 
# 2021.3.20  python -m cikuu.mq consume <queue_name>  cikuu.mq.hello  --host 192.168.1.24	--pwd rLGsGdr7bfYN56PHn41C091f
import pika, fire
class Mq:
	def __init__(self, host='172.17.0.1', port=5672, user='pigai', pwd='NdyX3KuCq', heartbeat=0): 
		self.credentials = pika.PlainCredentials(user, pwd)  #heartbeat_interval=50,
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host = host,port = port,virtual_host = '/',  credentials = self.credentials, heartbeat=heartbeat))
		self.channel	= self.connection.channel()

	def _callback(self, ch, method, properties, body):
		try:
			ch.basic_ack(delivery_tag = method.delivery_tag)
			pika.process(body.decode()) #cikuu.process(json.loads(body.decode())) # must be setattr outside !!!
		except Exception as e: 
			print("callback ex:", e, body.decode())
			self.channel.close()
			self.connection.close()	

	def consume_by(self, queue, process_path, prefetch_count=1, durable=True):
		''' python -m rabbitmq consume_by <queue_name>  cikuu.mq.hello  --host 192.168.1.24	--pwd rLGsGdr7bfYN56PHn41C091f '''
		print(f' [*] Waiting for messages from queue: {queue}, processed by {process_path}, To exit press CTRL+C', flush=True)
		x = __import__(process_path, fromlist=['process'])
		setattr(pika,'process', x.process)
		result	= self.channel.queue_declare(queue = queue, durable=durable)
		self.channel.basic_qos(prefetch_count=prefetch_count)
		self.channel.basic_consume(queue, self._callback) #, auto_ack=True ) #consumer_tag= str(os.getpid()) + "@" + socket.gethostname()
		self.channel.start_consuming()

	def consume(self, queue, func, prefetch_count=1, durable=True):
		''' 2023.4.28 '''
		print(f' [*] Waiting for messages from queue: {queue}, processed by {func}, To exit press CTRL+C', flush=True)
		result	= self.channel.queue_declare(queue = queue, durable=durable)
		self.channel.basic_qos(prefetch_count=prefetch_count)
		self.channel.basic_consume(queue, func) 
		self.channel.start_consuming()

if __name__ == '__main__': 
	fire.Fire(Mq) 



'''

from rabbitmq import Subscriber
import json

def on_message_callback(channel, method, properties, body):
    body_data = json.loads(body.decode())
    print(body_data)
    return

config = {'host': '192.168.201.79', 'port': 5672, 'callback': on_message_callback}

subscriber = Subscriber('dsk_rpc_v2_gec', '', config)
subscriber.setup()

def consume(queue_name, callback_func, host='192.168.1.214', port=5672, user='pigai', pwd='NdyX3KuCq', durable=True): 

	credentials = pika.PlainCredentials(user, pwd)  #heartbeat_interval=50,
	connection = pika.BlockingConnection(pika.ConnectionParameters(host = host,port = port,virtual_host = '/',  credentials = credentials))
	channel=connection.channel()

	result = channel.queue_declare(queue = queue_name, durable=durable) 
	print("queue is :", queue_name, flush=True)

	#x = __import__(func_path, fromlist=['callback'])
	channel.basic_consume(queue_name, callback_func)
	channel.start_consuming()
	#connection.close()
'''