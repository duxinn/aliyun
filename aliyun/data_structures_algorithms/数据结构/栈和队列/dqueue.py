
class Dqueue(object):
	'''双端队列'''

	def __init__(self):
		self.__queue = []

	def add_head(self, item):
		'''入队操作, 头部添加'''
		self.__queue.insert(0, item)

	def add_end(self, item):
		'''入队操作， 队尾添加'''
		return self.__queue.append(item)

	def pop_head(self):
		'''出队操作， 队首出队列'''
		return self.__queue.pop(0)

	def pop_end(self):
		'''出队操作， 队尾出队列'''
		return self.__queue.pop()

	def is_empty(self):
		'''判断是否为空'''
		return not self.__queue

	def size(self):
		'''返回队列的长度'''
		return len(self.__queue)


if __name__ == '__main__':
	dqueue = Dqueue()
	dqueue.add_head(8)
	dqueue.add_head(9)
	dqueue.add_end(7)
	dqueue.add_end(6)
	print(dqueue.pop_head())
	print(dqueue.pop_end())
	print(dqueue.size())
	print(dqueue.is_empty())