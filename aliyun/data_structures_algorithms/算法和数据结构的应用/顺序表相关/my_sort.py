'''排序算法的实现'''
import random


def bubble_sort(L):
    '''冒泡排序的实现
    O(n**2)
    稳定算法
    '''
    for i in range(len(L)):
        for j in range(len(L) - i - 1):
            if L[j] > L[j + 1]:
                L[j], L[j + 1] = L[j + 1], L[j]
    return L


def insert_sort(L):
    '''插入排序
    O(n**2)
    稳定
    '''
    count = len(L)
    for i in range(1, count):
        key = L[i]
        j = i - 1
        while j >= 0:
            if L[j] > key:
                L[j + 1] = L[j]
                L[j] = key
            else:
                break
            j -= 1
    return L


def quick_sort(L):
    '''快速排序
    O(nlogn)
    不稳定
    '''
    if len(L) < 2:
        return L
    key = L[0]
    lt = [x for x in L[1:] if x <= key]
    gt = [x for x in L[1:] if x > key]
    return quick_sort(lt) + [key] + quick_sort(gt)


def choice_sort(L):
    '''选择排序
    O(n**2)
    不稳定
    '''
    count = len(L)
    for i in range(count):
        min = i
        for j in range(i + 1, count):
            if L[j] < L[min]:
                min = j
        L[i], L[min] = L[min], L[i]
    return L


def shell_sort(L):
    """希尔排序
    O(n**2)
    不稳定
    """
    n = len(L)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            while i > 0:
                if L[i - gap] > L[i]:
                    L[i], L[i - gap] = L[i - gap], L[i]
                    i -= gap
                else:
                    break
        gap //= 2
    return L


def merge_sort(L):
	'''归并排序
	O(nlongn)
	稳定
	'''
	# 以下是归并过程中分解的过程
	n = len(L) // 2
	if n <= 1:
		return L
	left = merge_sort(L[:n])
	right = merge_sort(L[n:])
	# 以下是归并算法中的合并的过程
	result = []
	i, j = 0, 0
	while i < len(left) and j < len(right):
		if left[i] < right[j]:
			result.append(left[i])
			i += 1
		else:
			result.append(right[j])
			j += 1
	# 循环退出，将left和right中剩下的元素放入到列表中
	result += left[i:]
	result += right[j:]
	return result


if __name__ == '__main__':
    L = [x for x in map(lambda x:random.randrange(50), range(10))]
    print('原始列表: ', L)
    bubble_sort(L)
    print('冒泡排序: ', L)
    insert_sort(L)
    print('插入排序: ', L)
    print('快速排序: ', quick_sort(L))
    choice_sort(L)
    print('选择排序: ', L)
    shell_sort(L)
    print('希尔排序: ', L)
    print('归并排序: ', merge_sort(L))
