#!/usr/bin/python
#coding=UTF-8

import time

from ProcessManager import ProcessManager

pm = ProcessManager()

def test(t):
	for i in range(5):
		# print t
		time.sleep(1)
		print 'over'

for i in range(10):
	pm.addTask(test, args = (i,))

pm.start()
