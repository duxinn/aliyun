# 搜索是在一个项目集合中找到一个特定项目的算法过程。搜索通常的答案是真的或假的，因为该项目是否存在。
# 当然可以按照具体需求，返回值可以设为要查找的元素的下标，不存在返回-1
# 搜索的几种常见方法：顺序查找、二分法查找、二叉树查找、哈希查找
# 本文只是基于顺序表实现的查找算法，二叉树，哈希以后在介绍

def find(L, item):
	'''顺序查找，对排序的顺序表没有要求
	最优：O(1)
	最差：O(n)
	'''
	for i in L:
		if i == item:
			return True
	return False


def binary_search(L, item):
	'''二分查找，也叫折半查找，
	对排序的顺序表要求是：有序列表，不可以是链表（链表不能定位访问）
	最优：O(1)
	最差：O(logn)
	'''
	n = len(L)
	if n == 0:
		return False
	mid = n // 2
	if L[mid] == item:
		return True
	elif L[mid] < item:
		return binary_search(L[mid + 1:], item)
	else:
		return binary_search(L[:mid - 1], item)


if __name__ == '__main__':
	l = [x for x in range(10)]
	print(l)
	# 顺序查找测试
	print(find(l, 88))
	# 二分查找测试
	print(binary_search(l, 9))
