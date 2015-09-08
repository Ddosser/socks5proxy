#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import argparse


def cmdparse():
	parser = argparse.ArgumentParser(description = 'This is a socket proxy tool, support http|socks4|socks5 proxy.',
									usage = '%(prog)s [options] -u <url>')
	parser.add_argument('-l', '--listen', metavar = '', help = 'The address of proxy host to listen on, localhost as default', default = '127.0.0.1')
	parser.add_argument('-p', '--port', help = 'The port of proxy to listen on. port 1080 as default', type = int, default = '1080')
	parser.add_argument('-t', '--threads', help = 'defined threads for connecting', type = int, default = '1')
	parser.add_argument('-i', '--level', metavar = '', help = 'indicate the log level, INFO as default.', default = 'INFO')
	parser.add_argument('-u', '--url', metavar = '', help = 'The url contains tunnel script php|jsp|asp', required = True)
	return parser
def usage():
	parser = cmdparse()
	parser.print_help()
	sys.exit(1)

def get_args():
	parser = cmdparse()
	try:
		args = parser.parse_args()
	except:
		print "Using -h|--help option for help.\n"
		sys.exit(1)
	return args

def main():
	get_args()

if __name__ == "__main__":
	main()

