#!/usr/bin/python
#coding=UTF-8

import socket
from threading import Thread
import re
import json

# class protocol(object):
# 	"""docstring for ClassName"""
# 	def __init__(self, arg):
# 		super(ClassName, self).__init__()
# 		self.arg = arg

pProtocol = re.compile(r'^head:(\w+?):(\d+?)/(\d+?):(\d+?):(.+?):end$')

class Protocol(object):
	def __init__(self, pId = '', sId = 0, sNum = 0, size = 0, data = ''):
		self.pId = pId
		self.sId = sId
		self.sNum = sNum
		self.size = size
		self.data = data

class Listener(Thread):
	def __init__(self, connection, address, bufferSize = 1024):
		super(Listener, self).__init__()
		self.connection = connection
		self.address = address
		self.bufferSize = bufferSize
		self.dataDict = dict()

	'''head:aaa:1/10:3:{'aaa': 1}:end'''
	def analysis(self, data):
		m = pProtocol.search(data)
		if m is not None:
			pId = m.group(1)
			sId = int(m.group(2))
			sNum = int(m.group(3))
			size = int(m.group(4))
			data = m.group(5)
			p = Protocol(pId = pId, sId = sId, sNum = sNum, size = size, data = data)
			if pId not in self.dataDict:
				self.dataDict[pId] = dict()
			self.dataDict[pId][sId] = p
			if len(self.dataDict[pId]) == sNum:
				retP = Protocol(pId = pId, sId = sId, sNum = sNum, size = size)
				items = sorted(self.dataDict[pId].items(), key = lambda x: x[0])
				for i, d in items:
					retP.data = retP.data + d.data
				if size == len(retP.data):
					del self.dataDict[pId]
					retP.data = json.loads(retP.data)
					return retP
		return None

	def run(self):
		while True:
			buf = self.connection.recv(self.bufferSize)
			p = self.analysis(buf)
			if p is not None:
				print p.data
		self.connection.close()

class Server(object):
	def __init__(self, connectionType = 'long'):
		self.connectionType = connectionType
		self.num = 10
		self.timeout = 10
		self.bufferSize = 1024
		self.close = False
		self.addressDict = dict()

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind(('localhost', 8001))
		self.socket.listen(self.num)

	def close(self):
		self.close = True

	def setTimeout(self, timeout = 10):
		self.timeout = timeout

	def setNum(self, num = 10):
		self.num = num

	def closeServer(self, address):
		if address in self.addressDict:
			del self.addressDict[address]

	def run(self):
		while not self.close:
			connection, address = self.socket.accept()
			connection.settimeout(self.timeout)
			if address not in self.addressDict:
				self.addressDict[address] = Listener(connection, address)
				self.addressDict[address].start()
			print self.addressDict
			# self.listen(connection)

			# try:
			# 	buf = connection.recv(self.buffer)
			# 	print buf
			# 	if buf == '1':
			# 		connection.send('welcome to server!')
			# 	else:
			# 		connection.send('please go out!')
			# except socket.timeout:
			# 	print 'time out'
			# except:
			# 	print 
		# connection.close()

if __name__ == '__main__':
	Server().run()


# import socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.bind(('localhost', 8001))
# sock.listen(5)
# while True:
#     connection,address = sock.accept()
#     try:
#         connection.settimeout(5)
#         buf = connection.recv(1024)
#         if buf == '1':
#             connection.send('welcome to server!')
#         else:
#             connection.send('please go out!')
#     except socket.timeout:
#         print 'time out'
#     connection.close()