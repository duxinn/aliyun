'''基于链表的实现的栈结构
因为链表的头部操作的时间复杂度为O(1)
所以使用使用的时候都对头部进行操作
'''


class Node(object):
	def __init__(self, elem, next):
		self.elem = elem
		self.next = next


class Stack(object):

	def __init__(self):
		self.__top = None

	def is_empty(self):
		'''判断栈空'''
		return self.__top == None

	def top(self):
		'''返回当前栈顶的元素'''
		if self.is_empty():
			return
		return self.__top.elem

	def push(self, item):
		self.__top = Node(item, self.__top)

	def pop(self):
		'''出栈'''
		if self.is_empty():
			return
		p = self.__top
		self.__top = p.next
		return p.elem


if __name__ == '__main__':
	s = Stack()
	# 入栈测试
	s.push(81)
	s.push(82)
	#　判空测试
	print(s.is_empty())
	# 栈顶元素测试
	print(s.top())
	# 出栈测试
	print(s.pop(), end=' ')
	print(s.pop())
