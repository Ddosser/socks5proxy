1. urllib3
Linux:(debian)
	sudo apt-get install python-urllib3
if pip was installed on computer, using the following cocmmand to install urllib3.
	pip install urllib3

2. Usage
1)python DdosserSocks5Proxy.py -l [host] -p [port] -u <url>
2)editing proxychains configure file in /etc/proxychains.conf
	Last line "socks5 <host> <port>"
3)run command "proxychains <prog>" to use proxy
using "python DdosserSocks5Proxy.py --help" to get help.
