'''字符串kmp算法的实现，时间复杂度O(n)'''


def kmp_matching(t, p):
	'''采用kmp算法实现匹配（无回溯）
	t:目标串
	p:模式串
	'''
	# 求得用于kmp算法的next数组
	# pnext = find_next(p)
	# 优化之后的next数组
	pnext = find_next_better(p)
	# print(pnext)
	# m:模式串的长度，n:目标串的长度
	n, m = len(t), len(p)
	j, i = 0, 0
	# i==m 说明找到了
	while j < n and i < m:
		# 如果pnext数组中的i是-1，或者是模式串的字符和目标串的字符相等
		if i == -1 or t[j] == p[i]:
			i, j = i + 1, j + 1
		else:
			# 匹配失败，按照kmp算法的next数组中，当前失配元素下标处存的值进行移动
			i = pnext[i]
	# 匹配到返回下标
	if i == m:
		return j - i
	# 找不到，返回-1
	return -1


def find_next(p):
	'''用来求得kmp算法中的next数组'''
	i, k, m = 0, -1, len(p)
	pnext = [-1] * m
	while i < m - 1:
		if k == -1 or p[i] == p[k]:
			i, k = i + 1, k + 1
			pnext[i] = k
		else:
			k = pnext[k]
	return pnext


def find_next_better(p):
	'''kmp算法的优化，也就是对next数组的优化
	原理：让模式串右移的更远，匹配的执行的次数更少
	'''
	i, k, m = 0, -1, len(p)
	# 初始化next数组
	pnext = [-1]*m
	while i < m - 1:
		if k == -1 or p[i] == p[k]:
			i, k = i + 1, k + 1
			if p[i] == p[k]:
				pnext[i] = pnext[k]
			else:
				pnext[i] = k
		else:
			k = pnext[k]
	return pnext


if __name__ == '__main__':
	print(kmp_matching('abaabcab', 'bca'))








