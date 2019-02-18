from bin_tree import *

def deep_search(root):
	'''基于二叉树的深度优先遍历'''
	if root.elem is None:
		# 当根元素为空返回
		return
	print(root.elem, end=' ')
	if root.lchild:
		# 左子树不为空
		deep_search(root.lchild)
	if root.rchild:
		# 右子树不为空
		deep_search(root.rchild)


def width_search(root):
	'''基于二叉树的广度优先'''
	if root.elem is None:
		return
	q = [root]
	while q:
		# 弹出当前栈顶元素
		cur = q.pop(0)
		print(cur.elem, end=' ')
		# 左子树不为空
		if cur.lchild:
			q.append(cur.lchild)
		# 右子树不为空
		if cur.rchild:
			q.append(cur.rchild)



if __name__ == '__main__':
	# 测试
	tree = BinTree()
	for i in range(10):
		tree.add_to_tree(i)
	print('深度优先遍历： ', end='')
	deep_search(tree.root)
	print('\n广度优先遍历：', end=' ')
	width_search(tree.root)
