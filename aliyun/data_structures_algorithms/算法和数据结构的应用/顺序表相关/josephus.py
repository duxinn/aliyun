'''顺序表的应用，解决Josephus（环）问题'''


def josephus_list(n, k, m):
	'''通过固定list长度实现，出列的人即为0，否则为1
	n:总共有多少人
	k:开始的位置
	m:数m个（为1）
	'''
	people = list(range(1, n+1))
	i = k - 1
	# 遍历，保证n个人都会出来
	for num in range(n):
		# 计数器，当前数的数是多少
		count = 0
		while count < m:
			if people[i]:
				# 当前位置上不为0则加1
				count += 1
			if count == m:
				# 出列
				print(str(people[i])+'出列', end='  ')
				people[i] = 0
			# 每次后移，如果到了列表末尾，则从新开始
			i = (i + 1) % n
	print()


def josephus_listB(n, k, m):
	'''基于顺序表的解'''
	people = list(range(1, n+1))
	i = k - 1
	for num in range(n, 0, -1):
		# num代表的就是此时列表的长度
		i = (i + m -1) % num
		print(str(people.pop(i))+"出列", end="  ")


josephus_list(10, 2, 3)
josephus_listB(10, 2, 3)
