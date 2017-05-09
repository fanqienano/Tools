#!/usr/bin/python
#coding=UTF-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
from math import log
from PIL import Image, ImageDraw

# 创建决策节点
class DecideNode():
	def __init__(self, col = -1, value = None, result = None, tb = None, fb = None):
		self.col = col         # 待检验的判断条件所对应的列索引值
		self.value = value     # 为了使结果为true，当前列要匹配的值
		self.result = result   # 叶子节点的值
		self.tb = tb           # true下的节点
		self.fb = fb           # false下的节点

class Tree(object):

	def build(self, dataSet):
		print dataSet
		if len(dataSet) == 0:
			return DecideNode()

		# 初始化值
		best_gain = 0
		best_value = None
		best_sets = None
		best_col = None
		S = self.entropy(dataSet)

		# 获得最好的gain
		for col in range(len(dataSet[0]) - 1):
			total_value = {}	
			for data in dataSet:
				total_value[data[col]] = 1
			for value in total_value.keys():
				(set1, set2) = self.splitSet(dataSet, col, value)

				# 计算信息增益，将最好的保存下来
				s1 = float(len(set1)) / len(dataSet)
				s2 = float(len(set2)) / len(dataSet)
				gain = S - (s1 * self.entropy(set1) + s2 * self.entropy(set2))
				if gain > best_gain:
					best_gain = gain
					best_value = value
					best_col = col
					best_sets = (set1, set2)
		#创建节点
		if best_gain > 0:
			truebranch = self.build(best_sets[0])
			falsebranch = self.build(best_sets[1])
			return DecideNode(col = best_col, value = best_value, tb = truebranch, fb = falsebranch)
		else:
			return DecideNode(result = self.uniqueCount(dataSet))

	# 对数值型和离散型数据进行分类
	def splitSet(self, dataSet, column, value):
		splitfunction = None
		if isinstance(value, (int, float)):
			splitfunction = lambda x: x >= value
		else:
			splitfunction = lambda x: x == value
		set1 = [data for data in dataSet if splitfunction(data[column])]
		set2 = [data for data in dataSet if not splitfunction(data[column])]
		return (set1, set2)

	# 计算数据所包含的实例个数
	def uniqueCount(self, dataSet):
		result = {}
		for data in dataSet:
			r = data[len(data) - 1]
			result.setdefault(r, 0)
			result[r] += 1
		return result

	# 计算信息熵Entropy
	def entropy(self, dataSet):
		log2 = lambda x: log(x, 2)
		results = self.uniqueCount(dataSet)
		# Now calculate the entropy
		ent = 0.0
		for r in results.keys( ):
			p = float(results[r]) / len(dataSet)
			ent = ent - p * log2(p)
		return ent

	# 计算Gini impurity，CART用
	def giniImpurity(self, dataSet):
		total = len(dataSet)
		counts = self.uniqueCount(dataSet)
		imp = 0
		for k1 in counts:
			p1 = float(counts[k1]) / total
			for k2 in counts:
				if k1 == k2:
					continue
				p2 = float(counts[k2]) / total
				imp = imp + (p1 * p2)
		return imp

	# 后剪枝,设定一个阈值mingain来后剪枝，当合并后熵增加的值小于原来的值，就合并
	def prune(self, tree, mingain):
		if tree.tb.result == None:
			self.prune(tree.tb, mingain)
		if tree.fb.result == None:
			self.prune(tree.fb, mingain)

		if tree.tb.result != None and tree.fb.result != None:
			tb1, fb1 = [], []
			for v, c in tree.tb.result.items():
				tb1 = tb1 + [[v]] * c  #这里是为了跟row保持一样的格式，因为UniqueCount就是对这种进行的计算

			for v, c in tree.fb.result.items():
				fb1 = fb1 + [[v]] * c

			delta = self.entropy(tb1 + fb1) - (self.entropy(tb1) + self.entropy(fb1) / 2)
			if delta < mingain:
				tree.tb, tree.fb = None, None
				tree.result = self.uniqueCount(tb1 + fb1)

	# 计算方差(当输出为连续型的时候，用方差来判断分类的好或坏，决策树两边分别是比较大的数和比较小的数)
	# 可以通过后修剪来合并叶子节点
	def variance(self, dataSet):
		if len(dataSet) == 0:
			return 0
		data = [row[len(dataSet) - 1] for row in dataSet]
		mean = sum(data) / len(data)
		variance = sum([(d - mean) ** 2 for d in data]) / len(data)
		return variance

#对新实例进行查询
def classify(observation, tree):
	if tree.result != None:
		return tree.result
	else:
		v = observation[tree.col]
		branch = None
		if isinstance(v, (int, float)):
			if v >= tree.value:
				branch = tree.tb
			else:
				branch = tree.fb
		else:
			if v == tree.value:
				branch = tree.tb
			else:
				branch = tree.fb
		return classify(observation, branch)

#对缺失属性的数据进行查询
def mdclassify(observation, tree):
	if tree.result != None:
		return tree.result

	if observation[tree.col] == None:
		tb, fb = mdclassify(observation, tree.tb), mdclassify(observation, tree.fb)  #这里的tr跟fr实际是这个函数返回的字典
		tbcount = sum(tb.values())
		fbcount = sum(fb.values())
		tw = float(tbcount) / (tbcount + fbcount)
		fw = float(fbcount) / (tbcount + fbcount)

		result = {}
		for k, v in tb.items():
			result.setdefault(k, 0)
			result[k] = v * tw
		for k, v in fb.items():
			result.setdefault(k, 0)
			result[k] = v * fw
		return result
	else:
		v = observation[tree.col]
		branch = None
		if isinstance(v, (int, float)):
			if v >= tree.value:
				branch = tree.tb
			else:
				branch = tree.fb
		else:
			if v == tree.value:
				branch = tree.tb
			else:
				branch = tree.fb
		return mdclassify(observation, branch)

# 打印文本形式的tree
def PrintTree(tree, indent = ''):
	if tree.result != None:
		print str(tree.result)
	else:
		print '%s:%s?'%(tree.col, tree.value)
		print indent, 'T->',
		PrintTree(tree.tb, indent + '  ')
		print indent, 'F->',
		PrintTree(tree.fb, indent + '  ')

# 打印图表形式的tree
def drawtree(tree,jpeg = 'tree.jpg'):
	w = getwidth(tree) * 100
	h = getdepth(tree) * 100 + 120
	img = Image.new('RGB', (w, h), (255, 255, 255))
	draw = ImageDraw.Draw(img)
	drawnode(draw, tree, w / 2, 20)
	img.save(jpeg, 'JPEG')

def getwidth(tree):
	if tree.tb == None and tree.fb == None:
		return 1
	return getwidth(tree.tb) + getwidth(tree.fb)

def getdepth(tree):
	if tree.tb == None and tree.fb == None:
		return 0
	return max(getdepth(tree.tb), getdepth(tree.fb)) + 1

def drawnode(draw,tree,x,y):
	if tree.result == None:
	# Get the width of each branch
		w1 = getwidth(tree.fb) * 100
		w2 = getwidth(tree.tb) * 100
		# Determine the total space required by this node
		left = x - (w1 + w2) / 2
		right = x + (w1 + w2) / 2
		# Draw the condition string
		draw.text((x - 20, y - 10), str(tree.col) + ':' + str(tree.value), (0, 0, 0))
		# Draw links to the branches
		draw.line((x, y, left + w1 / 2, y + 100), fill = (255, 0, 0))
		draw.line((x, y, right - w2 / 2, y + 100), fill = (255, 0, 0))
		# Draw the branch nodes
		drawnode(draw, tree.fb, left + w1 / 2, y + 100)
		drawnode(draw, tree.tb, right - w2 / 2, y + 100)
	else:
		txt = ' \n'.join(['%s:%d'%v for v in tree.result.items( )])
		draw.text((x - 20, y), txt, (0, 0, 0))

if __name__ == '__main__':
	dataSet = [
	['slashdot','USA','yes',18,'None'],
	['google','France','yes',23,'Premium'],
	['digg','USA','yes',24,'Basic'],
	['kiwitobes','France','yes',23,'Basic'],
	['google','UK','no',21,'Premium'],
	['(direct)','New Zealand','no',12,'None'],
	['(direct)','UK','no',21,'Basic'],
	['google','USA','no',24,'Premium'],
	['slashdot','France','yes',19,'None'],
	['digg','USA','no',18,'None'],
	['google','UK','no',18,'None'],
	['kiwitobes','UK','no',19,'None'],
	['digg','New Zealand','yes',12,'Basic'],
	['slashdot','UK','no',21,'None'],
	['google','UK','yes',18,'Basic'],
	['kiwitobes','France','yes',19,'Basic']
	]
	['google', None, 'yes', None]
	t = Tree()
	tree = t.build(dataSet)
	# PrintTree(tree)
	drawtree(tree, jpeg = 'tree0.jpg')
	t.prune(tree, 0.1)
	# PrintTree(tree)
	drawtree(tree, jpeg = 'tree1.jpg')
	t.prune(tree, 1)
	# PrintTree(tree)
	drawtree(tree, jpeg = 'tree2.jpg')
	# drawtree(tree)
	mdclassify(['google', None, 'yes', None], tree)