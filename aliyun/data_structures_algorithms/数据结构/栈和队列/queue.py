
class Queue(object):
	'''队列的实现，通过list存储数据'''

	def __init__(self):
		self.__queue = []

	def enqueue(self, item):
		'''入队操作'''
		self.__queue.append(item)

	def dequeue(self):
		'''出队操作'''
		return self.__queue.pop(0)

	def is_empty(self):
		'''判断是否为空'''
		return not self.__queue

	def size(self):
		'''返回队列的长度'''
		return len(self.__queue)


if __name__ == '__main__':
	queue = Queue()
	queue.enqueue(5)
	queue.enqueue(4)
	queue.enqueue(3)
	queue.enqueue(2)
	print(queue.size())
	print(queue.is_empty())
	print(queue.dequeue())
