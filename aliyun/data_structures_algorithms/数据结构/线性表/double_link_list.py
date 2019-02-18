'''双向链表 '''


class Node(object):
	'''结点类
	args:
		item: 数据
		_prev: 结点的前驱
		_next: 结点的后继
	'''
	def __init__(self, elem):
		self.elem = elem
		self._prev = None
		self._next = None


class DLinkList(object):
	'''双向链表'''
	def __init__(self, node=None):
		'''初始化双向链表'''
		if node:
			node = Node(node)
		self.__head = node

	def is_empty(self):
		'''判断双向链表是否为空'''
		return self.__head == None

	def length(self):
		'''链表长度'''
		count = 0
		if self.is_empty():
			return count
		else:
			cur = self.__head
			while cur != None:
				count += 1
				cur = cur._next
			return count

	def travel(self):
		'''遍历链表'''
		cur = self.__head
		while cur != None:
			print(cur.elem, end=" ")
			cur = cur._next
		print()

	def add(self, item):
		'''链表头部添加, 头插法'''
		node = Node(item)
		if self.is_empty():
			self.__head = node
		else:
			node._next = self.__head
			self.__head._prev = node
			self.__head = node

	def append(self, item):
		'''链表尾部添加'''
		node = Node(item)
		if self.is_empty():
			self.__head = node
		else:
			cur = self.__head
			while cur._next != None:
				cur = cur._next
			cur._next = node
			node._prev = cur

	def insert(self, pos, item):
		'''指定位置添加'''
		if pos <= 0:
			self.add(item)
		elif pos > self.length() - 1:
			self.append(item)
		else:
			node = Node(item)
			count = 0
			cur = self.__head
			while count < pos - 1:
				count += 1
				cur = cur._next
			node._prev = cur
			node._next = cur._next
			cur._next._prev = node
			cur._next = node

	def remove(self, item):
		'''删除节点'''
		if self.is_empty():
			return
		cur = self.__head
		if cur.elem == item:
			# 如果是首结点的元素
			if cur._next == None:
				# 表示只有一个元素
				self.__head = None
			else:
				cur._next._prev = None
				self.__head = cur._next
			return
		while cur._next != None:
			if cur.elem == item:
				cur._prev._next = cur._next
				cur._next._prev = cur._prev
				return
			cur = cur._next
		# 删除的是最后一个结点元素
		cur._prev._next = None

	def search(self,item):
		'''查找节点是否存在'''
		if self.is_empty():
			return False
		cur = self.__head
		while cur != None:
			if cur.elem == item:
				return True
			cur = cur._next
		return False


if __name__ == '__main__':
	dll = DLinkList(9)
	# print(dll.is_empty())
	# print(dll.length())
	# dll.travel()
	# 测试add()
	dll.add(7)
	print('链表长度：', dll.length())
	dll.travel()
	# 测试append()
	dll.append(8)
	dll.append(6)
	dll.append(5)
	print('链表长度为：', dll.length())
	dll.travel()
	# 测试insert()
	dll.insert(0, 1)
	dll.insert(6, 4)
	dll.insert(4, 7)
	print('链表长度为', dll.length())
	dll.travel()
	# 测试remove()
	dll.remove(1)
	print("删除前：")
	dll.travel()
	dll.remove(6)
	print('链表长度为', dll.length())
	dll.travel()
	# 测试search()
	print(dll.search(4))

