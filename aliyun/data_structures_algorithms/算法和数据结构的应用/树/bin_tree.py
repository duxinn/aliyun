

class Node:
	'''定义节点类型'''
	def __init__(self, elem):
		'''初始化节点类'''
		self.elem = elem
		self.lchild = None
		self.rchild = None


class BinTree:
	'''定义二叉树类'''
	def __init__(self, root=None):
		# 初始化一颗空树
		self.root = root

	def is_empty(self):
		'''判断是否为空树'''
		return self.root == None

	def add_to_tree(self, item):
		'''往树里边添加节点'''
		node = Node(item)
		if self.is_empty():
			self.root = node
		else:
			# 作为缓冲
			q = [self.root]
			# 缓冲区不为空
			while q:
				# 将当前缓冲区的节点弹出
				cur_node = q.pop(0)
				# 判断左子树空
				if not cur_node.lchild:
					cur_node.lchild = node
					return self
				else:
					q.append(cur_node.lchild)
				# 判断右子树是否空
				if not cur_node.rchild:
					cur_node.rchild = node
					return self
				else:
					q.append(cur_node.rchild)



