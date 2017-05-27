#!/usr/bin/python
#coding=UTF-8

from Server import Server
import time

def test(data):
	print data, time.time()
	return 'test ok'

s = Server(host = 'localhost', port = 8000, socketType = 'short')
s.setHandle({'test': test})
s.run()