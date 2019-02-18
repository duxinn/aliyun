'''基于栈的应用，检查文文本括号是否匹配'''
# 导入栈数据结构
from stack_model import Stack


def check_parens(text):
	# 括号的所有集合
	parens = '()[]{}'
	# 开括号的所有集合
	open_parens = '([{'
	# 匹配关系的字典
	parens_dic = {')':'(', ']':'[', '}':'{'}

	def parens_yiled(text):
		'''定义括号生成器，找出文本中的括号，以及在文本中的位置'''
		i, text_len = 0, len(text)
		while True:
			while i < text_len and text[i] not in parens:
				# 跳过和括号无关的字符
				i += 1
			if i >= text_len:
				return
			# 生成器生成括号和当前的位置
			yield text[i], i
			i += 1

	s = Stack()
	for pr, i in parens_yiled(text):
		if pr in open_parens:
			# 如果当前的文本为开括号
			s.push(pr)
		elif s.pop() != parens_dic[pr]:
			# 当前文本为闭括号,将当前栈顶的括号拿出来匹配
			print('%d处括号不匹配'%i)
			return False
	# 所有括号匹配成功
	print('所有括号匹配正确')
	return True


if __name__ == '__main__':
	text = 'afsheufh{sdfnafe(dnsajfnjds)dsmfakdf[dsafndf]sfak]'
	check_parens(text)
	text1 = 'afsheufh{sdfnafe(dnsajfnjds)dsmfakdf[dsafndf]sfak}'
	check_parens(text1)


