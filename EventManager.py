#!/usr/bin/python
#coding=UTF-8

class Event(object):
	'''
	自定义事件
	name: 事件名
	data: 事件分发数据 list
	'''
	def __init__(self, name, data):
		self.name = name
		self.data = data

class EventManager(object):
	'''
	事件管理
	'''
	def __init__(self):
		self.eventDict = dict()

	def hasListener(self, event, listener):
		'''
		判断是已经有事件监听
		event: 事件 Event object
		listener: 监听方法
		'''
		return event.name in self.eventDict and listener in self.eventDict[event.name]

	def addEventListener(self, event, listener):
		'''
		添加事件监听器
		event: 事件 Event object
		listener: 监听方法
		'''
		if event.name not in self.eventDict:
			self.eventDict[event.name] = []
		self.eventDict[event.name].append(listener)

	def removeEventListener(self, event, listener):
		'''
		已出事件监听器
		event: 事件 Event object
		listener: 监听方法
		'''
		if self.hasListener(event, listener):
			self.eventDict[event.name].remove(listener)

	def dispatch(self, event):
		'''
		开始分发事件
		event: 事件 Event object
		listener: 监听方法
		'''
		if event.name in self.eventDict:
			for listener in self.eventDict[event.name]:
				listener(*event.data)