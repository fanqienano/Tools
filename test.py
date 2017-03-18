#!/usr/bin/python
#coding=UTF-8

import time

from ProcessManager import ProcessManager

pm = ProcessManager()

def test(t):
	for i in range(3):
		# print t
		time.sleep(1)
		# print 'over'

for i in range(30):
	pm.addTask(test, args = (i,))

pm.start()
pm.close()
pm.wait()
print 111