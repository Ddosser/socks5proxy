#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import httplib
import urllib3
import urlparse
from socket import *
from threading import Thread 
from time import sleep

#customer libs
from lib.cmdparser import get_args
from lib.proxyparser import *

version = '1.0'
author = 'Ddosser'
mail = 'arseswilliam@gmail.com'

#OUT_FORMAT
# 30 BLACK
# 31 RED
# 32 GREEN
# 33 YELLOW
# 34 BLUE
# 35 
# 36
# 37 WHITE
GREEN = '\033[1;32m'
RED = '\033[1;31m'
WHITE = '\033[1;37m'
DEFAULT = '\033[0m'
END = '\033[0m'

class Session(Thread):
	def __init__(self, cltsock, conn_url):
		Thread.__init__(self, name = 'session_thread', args = ())
		self.__sock = cltsock
		self.__conn_url = conn_url

		o = urlparse.urlparse(self.__conn_url)
		self.__httpScheme = o.scheme
		self.__host = o.netloc.split(':')[0]			#some bug 
		self.__path = o.path
		self.__cookie = None
		try:
			self.__port = o.port
		except:
			if self.__httpScheme == 'https':
				self.__port = 443
			else:
				self.__port = 80	
		self.__parser = Proxyparser(self.__conn_url)	

	def run(self):
		if self.__parser.handleSocks(self.__sock):
			r = Thread(target = self.reader, name = 'read_thread', args = ())
			r.start()
			w = Thread(target = self.writer, name = 'write_thread', args = ())
			w.start()

			r.join()
			w.join()

	def reader(self):
		conn = urllib3.PoolManager()
		while True:
			data = None
			headers = { 'X-CMD':'READ',
						'Cookie':self.__cookie,
						'Connection':'Keep-Alive'
			}
			response = conn.urlopen('POST', self.__conn_url + '?cmd=read', headers = headers, body = '')

			if response.status == 200:
				if response.getheader('x-status') == 'OK':
					cookie = response.getheader('set-cookie')
					if cookie is not None:
						self.__cookie = cookie
					data = response.data
				else:
					data = None
			if data == None or data == '':
				break;
			if len(data)== 0:
				continue
			out_format("[*]Reader: reading target url data ok", 'OK')
			out_format("[*]DATA: {}".format(data), 'INFO')
			self.__sock.send(data)
		self.__parser.closeRemoteSession()
		try:
			self.__sock.close()
		except:
			out_format("[*] Connected: Proxy client closed.", 'ERROR')



	def writer(self):
		conn = urllib3.PoolManager()
		while True:
			try:
				self.__sock.settimeout(1)
				data = self.__sock.recv(8192)
				if not data: 
					break;

				headers = { 'X-CMD':'FORWARD', 
							'Cookie':self.__cookie,
							'Content-type':'application/octet-stream',
							'Connection':'Keep-Alive'
				}

				response = conn.urlopen('POST', self.__conn_url + '?cmd=forward', headers = headers, body = data)
				if response.status == 200:
					status = response.getheader('x-status')
					if status == 'OK':
						cookie = response.getheader('set-cookie')
						if cookie is not None:
							self.__cookie = cookie
					else:
						#log
						break
				else:
					out_format('[*] Writer: response code: {}'.format(response.status), 'ERROR')
					break
			except timeout:
				continue
			except Exception,ex:
				out_format(ex,"ERROR")
				break
		self.__parser.closeRemoteSession()
		try:
			self.__sock.close()
		except:
			out_format('Socket was already closed.','ERROR')


def out_format(message, type = None):
	if type == 'INFO':
		color = WHITE
	elif type == 'ERROR':
		color = RED
	elif type == 'OK':
		color = GREEN
	elif type == None:
		color = DEFAULT

	print color + str(message) + END

def setup_connect():
	args = get_args()
	lhost = args.listen
	lport = args.port
	#url = args.url

	srvsock = socket(AF_INET, SOCK_STREAM)
	srvsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	srvsock.bind((lhost, lport))
	srvsock.listen(1024)
	out_format("[*]Server: listen on {}:{}\n".format(lhost, lport), 'OK')
	while True:
		try:
			sock, addr = srvsock.accept()
			sock.settimeout(5)
			out_format("[*]Connected: Connected from {}:{}".format(addr[0], addr[1]), 'OK')
			t = Session(sock, args.url)
			t.start()
			out_format('[*]' + t.getName() + 'Loading OK', 'OK')
		except Exception,ex:
			out_format(ex, 'ERROR')
			break
		except Exception,e:
			print e
			#break
	srvsock.close()


def main():
	setup_connect()

if __name__ == "__main__":
	main()

