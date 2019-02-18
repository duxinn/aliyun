'''基于list实现的优先队列'''


class Prioque:
	'''小的代表优先级高'''
	def __init__(self, elist=[]):
		self.__elem = list(elist)
		# 将列表进行从大到小排序
		self.__elem.sort(reverse=True)

	def enqueue(self, e):
		'''入队操作'''
		i = len(self.__elem) - 1
		while i >= 0:
			if e >= self.__elem[i]:
				i -= 1
			else:
				break
		self.__elem.insert(i+1, e)

	def is_empty(self):
		'''判断队列是否为空'''
		return not self.__elem


	def dequeue(self):
		'''出队操作'''
		if self.is_empty():
			return
		return self.__elem.pop()

	def peek(self):
		'''查看当前优先级最高的元素'''
		return self.__elem[-1]


if __name__ == '__main__':
	prioque = Prioque()
	print(prioque.is_empty())
	prioque.enqueue(5)
	prioque.enqueue(3)
	prioque.enqueue(6)
	print(prioque.is_empty())
	p = prioque.peek()
	print(p)
	print(prioque.dequeue())
	print(prioque.dequeue())
	print(prioque.dequeue())