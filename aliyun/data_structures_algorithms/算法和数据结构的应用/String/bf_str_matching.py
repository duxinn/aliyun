'''朴树（BF）算法，事件复杂度是（m*n）'''


def naive_matching(t, p):
	'''使用朴素匹配算法
	t:模式串
	p:目标串
	'''
	m, n = len(t), len(p)
	i, j = 0, 0
	while i < m and j < n:
		if j == n - m + 1 and i == 0 and t[i] != p[j]:
			# 当匹配到只剩下模式串长度了，第一位还不一样就终止，找不到
			return -1
		if t[i] == p[j]:
			i += 1
			j += 1
		else:
			j = j - i + 1
			i = 0
	# 找到了返回目标串刚开始匹配上的下标
	if i == m:
		return j - i
	# 表示没有找到
	return -1


if __name__ == '__main__':
	print(naive_matching('sa', 'fdsafefwabc'))

