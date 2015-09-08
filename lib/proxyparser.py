#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import httplib
import urllib3
import urlparse
from socket import *
#from threading import Thread 
from time import sleep

# Constants
SOCKTIMEOUT = 5
RESENDTIMEOUT=300
VER="\x05"
METHOD="\x00"
SUCCESS="\x00"
SOCKFAIL="\x01"
NETWORKFAIL="\x02"
HOSTFAIL="\x04"
REFUSED="\x05"
TTLEXPIRED="\x06"
UNSUPPORTCMD="\x07"
ADDRTYPEUNSPPORT="\x08"
UNASSIGNED="\x09"

class Proxyparser:
    def __init__(self, conn_url):
        self.__conn_url = conn_url
        o = urlparse.urlparse(self.__conn_url)
        self.__httpScheme = o.scheme
        self.__host = o.netloc.split(':')[0]            #some bug 
        self.__path = o.path
        self.__cookie = None
        try:
            self.__port = o.port
        except:
            if self.__httpScheme == 'https':
                self.__port = 443
            else:
                self.__port = 80    
        if o.scheme == "http":
            self.__httpScheme = urllib3.HTTPConnectionPool
        else:
            self.__httpScheme = urllib3.HTTPSConnectionPool
    def __parseSocks5(self,sock):
        nmethods,methods=(sock.recv(1),sock.recv(1))
        sock.sendall(VER+METHOD)
        ver=sock.recv(1)
        if ver=="\x02": # this is a hack for proxychains
            ver,cmd,rsv,atyp=(sock.recv(1),sock.recv(1),sock.recv(1),sock.recv(1))
        else:
            cmd,rsv,atyp=(sock.recv(1),sock.recv(1),sock.recv(1))
        target = None
        targetPort = None
        if atyp=="\x01":# IPv4
            # Reading 6 bytes for the IP and Port
            target = sock.recv(4)
            targetPort = sock.recv(2)
            target =".".join([str(ord(i)) for i in target])
        elif atyp=="\x03":# Hostname
            targetLen = ord(sock.recv(1)) # hostname length (1 byte)
            target = sock.recv(targetLen)
            targetPort  = sock.recv(2)
            target = "".join([unichr(ord(i)) for i in target])
        elif atyp=="\x04":# IPv6
            target = sock.recv(16)
            targetPort = sock.recv(2)
            tmp_addr=[]
            for i in xrange(len(target)/2):
                tmp_addr.append(unichr(ord(target[2*i])*256+ord(target[2*i+1])))
            target=":".join(tmp_addr)
        targetPort = ord(targetPort[0])*256+ord(targetPort[1])            

        if cmd=="\x01":#CONNECT
            serverIp = target
            try:
                serverIp = gethostbyname(target)
            except:
                pass
            serverIp="".join([chr(int(i)) for i in serverIp.split(".")])
            self.cookie = self.setupRemoteSession(target,targetPort)
            if self.cookie:
                sock.sendall(VER+SUCCESS+"\x00"+"\x01"+serverIp+chr(targetPort/256)+chr(targetPort%256))
                return True
            else:
                sock.sendall(VER+REFUSED+"\x00"+"\x01"+serverIp+chr(targetPort/256)+chr(targetPort%256))
        
        
    def handleSocks(self,sock):
        # This is where we setup the socks connection
        ver = sock.recv(1)
        if ver == "\x05":
            return self.__parseSocks5(sock)
        else:
            print 'Not support this proxy.'

    def setupRemoteSession(self,target,port):
        headers = {"X-CMD": "CONNECT", "X-TARGET": target, "X-PORT": port}
        self.target = target
        self.port = port
        cookie = None
        conn = self.__httpScheme(host=self.__host, port=self.__port)
        #response = conn.request("POST", self.httpPath, params, headers)
        response = conn.urlopen('POST', self.__conn_url+"?cmd=connect&target=%s&port=%d" % (target,port), headers=headers, body="")
        if response.status == 200:
            status = response.getheader("x-status")
            if status == "OK":
                cookie = response.getheader("set-cookie")
        conn.close()
        return cookie       
            
    def closeRemoteSession(self):
        headers = {"X-CMD": "DISCONNECT", "Cookie":self.cookie}
        #headers = {"Cookie":self.cookie}
        params=""
        conn = self.__httpScheme(host=self.__host, port=self.__port)
        response = conn.request("POST", self.__path+"?cmd=disconnect", params, headers)
        if response.status == 200:
            print "[%s:%d] Connection Terminated" % (self.target,self.port)
        conn.close()