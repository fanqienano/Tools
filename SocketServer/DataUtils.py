#!/usr/bin/python
#coding=UTF-8

import re

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from Crypto import Random

pProtocol = re.compile(r'^head:(\w+?):(\w+?):(\d+?)/(\d+?):(\d+?):([\s|\S]+?):end$')
pProtocolStart = re.compile(r'^head:(\w+?):text:1/1:(\d+?):start:end$')
pProtocolFinish = re.compile(r'^head:(\w+?):text:1/1:(\d+?):finish:end$')
pProtocolHead = re.compile(r'^(\w{19})\|(\d{10})\|(.{19})$')

HeadSize = 160

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


def analysis(data):
	m = pProtocol.match(data)
	if m is not None:
		pId = m.group(1)
		dataType = m.group(2)
		sId = int(m.group(3))
		sNum = int(m.group(4))
		size = int(m.group(5))
		data = m.group(6)
		p = Protocol(pId = pId, sId = sId, sNum = sNum, size = size, data = data, dataType = dataType)
		return p, 'ok'
	else:
		return None, 'error'

def makeHead(pId, msg, path):
	return '%s|%s|%s'%(pId, str(len(msg)).zfill(10), path.rjust(19))

Key = '0123456789abcdef'
Mode = AES.MODE_CBC

def encryption(text):
	iv = Random.new().read(AES.block_size)
	cryptor = AES.new(Key, Mode, iv)
	text = text + (AES.block_size - len(text) % AES.block_size) * '*'
	ciphertext = cryptor.encrypt(text)
	return b2a_hex(iv + ciphertext)
		
def decryption(text):
	ciphertext = a2b_hex(text)
	iv = ciphertext[0: AES.block_size]
	ciphertext = ciphertext[AES.block_size: len(ciphertext)]
	cryptor = AES.new(Key, Mode, iv)
	plaintext = cryptor.decrypt(ciphertext)
	return plaintext.rstrip('*')
