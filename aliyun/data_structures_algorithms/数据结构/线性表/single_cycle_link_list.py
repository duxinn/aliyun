# coding:utf8
'''单项循环链表'''


class Node(object):
	'''结点类'''
	def __init__(self, elem):
		# 用来保存元素
		self.elem = elem
		# 用来保存下一个元素的地址
		self.next_ = None


class SingleCycleLinkList(object):
	'''单向循环链表类'''
	def __init__(self, node=None):
		# 将初始化传入的node转换为Node类型
		if node:
			node = Node(node)
			node.next_ = node
		self.__head = node


	def is_empty(self):
		'''判断链表是否为空'''
		return self.__head == None

	def length(self):
		'''求单项循环链表的长度'''
		#如果链表为空
		count = 1
		cur = self.__head
		if self.is_empty():
			return count - 1
		while cur.next_!= self.__head:
			count += 1
			cur = cur.next_
		return count

	def travel(self):
		'''遍历单项循环链表'''
		# 判断当前链表是否为空
		if self.is_empty():
			# 为空
			return
		cur = self.__head
		while cur.next_ != self.__head:
			print(cur.elem, end=" ")
			cur = cur.next_
		print(cur.elem)

	def add(self, item):
		'''单链表头部添加，头插法'''
		node = Node(item)
		if self.is_empty():
			# 如果链表为空
			self.__head = node
			node.next_ = self.__head
		else:
			# 不为空头插法
			node.next_ = self.__head
			cur = self.__head
			while cur.next_ != self.__head:
				cur = cur.next_
			cur.next_ = node
			# head指向新添加的node
			self.__head = node

	def append(self, item):
		'''尾插法'''
		node = Node(item)
		if self.is_empty():
			# 链表为空和头插法一样
			self.__head = node
			node.next_ = self.__head
		else:
			cur = self.__head
			while cur.next_ != self.__head:
				cur = cur.next_
			cur.next_ = node
			node.next_ = self.__head

	def insert(self, position, item):
		'''任意位置插入'''
		if position <= 0:
			# 头插法
			self.add(item)
		elif position > self.length()-1:
			# 尾插法
			self.append(item)
		else:
			node = Node(item)
			cur = self.__head
			count = 0
			while count < position-1:
				count += 1
				cur = cur.next_
			node.next_ = cur.next_
			cur.next_ = node

	def remove(self, item):
		'''删除第一次出现的元素'''
		if self.is_empty():
			return
		cur = self.__head
		# 删除的元素是头结点元素
		if cur.elem == item:
			# 链表只有一个元素
			if cur.next_ == self.__head:
				self.__head = None
			else:
				# 链表不止一个元素,找到元素的最后一个节点
				while cur.next_ != self.__head:
					cur = cur.next_
				cur.next_ = self.__head.next_
				self.__head = self.__head.next_
		else:
			pre = self.__head
			# 删除的元素不是头结点
			while cur.next_ != self.__head:
				# 找到要删除的元素
				if cur.elem == item:
					# 删除
					pre.next_ = cur.next_
					return
				else:
					pre = cur
					cur = cur.next_
			# 如果是尾部删除
			if cur.elem == item:
				pre.next_ = cur.next_

	def search(self, item):
		'''查找存在返回True,不存在返回False'''
		if self.is_empty():
			return False
		cur = self.__head
		#　就一个元素
		if cur.elem == item:
			return True
		# 链表有多个元素
		while cur.next_ != self.__head:
			cur = cur.next_
			if cur.elem == item:
				return True
		return False


if __name__ == '__main__':
	scl = SingleCycleLinkList()
	print(scl.is_empty())
	print(scl.length())
	scl.travel()
	# 测试add()
	scl.add(8)
	scl.travel()
	print('链表长度:',scl.length())
	scl.add(9)
	scl.travel()
	print('链表长度:', scl.length())
	# 测试append
	scl.append(2)
	scl.append(1)
	scl.travel()
	print('链表长度:', scl.length())
	# 测试insert()
	scl.insert(3,100)
	scl.travel()
	print('链表长度:', scl.length())
	# 测试remove()
	scl.remove(100)
	scl.remove(9)
	scl.remove(2)
	scl.travel()
	print('链表长度:', scl.length())
	print(scl.search(5))
