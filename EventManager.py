#!/usr/bin/python
#coding=UTF-8

class Event(object):
	def __init__(self, name, data):
		self.name = name
		self.data = data

class EventManager(object):
	def __init__(self):
		self.eventDict = dict()

	def hasListener(self, event, listener):
		return event.name in self.eventDict and listener in self.eventDict[event.name]

	def addEventListener(self, event, listener):
		if event.name not in self.eventDict:
			self.eventDict[event.name] = []
		self.eventDict[event.name].append(listener)

	def removeEventListener(self, event, listener):
		if self.hasListener(event, listener):
			self.eventDict[event.name].remove(listener)

	def dispatch(self, event):
		if event.name in self.eventDict:
			for listener in self.eventDict[event.name]:
				listener(*event.data)