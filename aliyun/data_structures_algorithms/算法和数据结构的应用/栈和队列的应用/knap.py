'''背包问题的解决方案'''
# 基于栈或者递归求得的简单背包问题的解决
# 问题原型：
# 	一个背包可以放入重量为weight的物品，现在有n件物品的集合S
#	物品的重量分别为w0,w1,...w(n-1),问题，是否能从中选择若干件物品，使得和真好等于weight

def knap(weight, wlist, n):
	'''简单背包问题的递归求解
	weight:背包所能容纳的最大重量
	wlist:记录物品重量的列表
	n:物品数量
	'''
	if weight == 0:
		# 总的重量剩余为0，说明有解
		return True
	if weight < 0 or (weight > 0 and n < 1):
		# 总重量剩余小于0，或者是大于0并且物品数量小于0，无解
		return False
	if knap(weight-wlist[n-1], wlist, n-1):
		# 每次递归选取最后一个，所以背包此时的剩余总质量就是weight-wlist[n-1]
		print('选取第'+str(n) + "个e:", wlist[n - 1])
		return True
	if knap(weight, wlist, n-1):
		# 不选取最后一件物品时有解
		return True
	else:
		return False


if __name__ == '__main__':
	weight = 10
	wlist = [8,1,3,4,5]
	n = 5
	print(knap(weight, wlist, n))