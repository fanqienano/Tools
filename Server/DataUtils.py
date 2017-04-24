#!/usr/bin/python
#coding=UTF-8

import re

pProtocol = re.compile(r'^head:(\w+?):(\w+?):(\d+?)/(\d+?):(\d+?):([\s|\S]+?):end$')

class Protocol(object):
	def __init__(self, pId = '', sId = 0, sNum = 0, size = 0, data = '', dataType = 'text'):
		self.pId = pId
		self.sId = sId
		self.sNum = sNum
		self.size = size
		self.data = data
		self.dataType = dataType

	def __str__(self):
		return 'head:{pId}:{dataType}:{sId}/{sNum}:{size}:{data}:end'.format(pId = self.pId, dataType = self.dataType, sId = self.sId, sNum = self.sNum, size = self.size, data = self.data)