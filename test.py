#!/usr/bin/python
#coding=UTF-8

import time

from TaskManager import ProcessManager

pm = ProcessManager()

def test(t):
	print t
	time.sleep(3)
	print 'over'

for i in range(30):
	pm.addTask(test, args = (i,))

pm.start()
pm.close()
pm.wait()
print 111