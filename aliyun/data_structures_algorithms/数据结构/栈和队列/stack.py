'''栈的实现,通过python中的list来实现数据存储'''


class Stack(object):

	def __init__(self):
		'''初始化一个空栈'''
		self._stack = []

	def push(self, item):
		'''添加一个新元素，入栈'''
		self._stack.append(item)

	def pop(self):
		'''出栈操作'''
		return self._stack.pop()

	def peek(self):
		'''返回栈顶元素'''
		return self._stack[-1]

	def is_empty(self):
		'''判断栈是否为空'''
		return not self._stack

	def size(self):
		'''返回栈的元素个数'''
		return len(self._stack)


if __name__ == '__main__':
	stack = Stack()
	stack.push(5)
	stack.push(4)
	stack.push(3)
	stack.push(2)
	stack.push(1)
	print(stack.is_empty())
	print(stack.size())
	print(stack.pop())
	print(stack.pop())
	print(stack.peek())
