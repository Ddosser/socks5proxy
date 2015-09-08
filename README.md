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
3.arguments.
-l [host] listening on the "host"
-p [port] listening on the "port"
-u <url> the url is the file "tunnel.php" uploaded location address. how to do that? I don't know.
-h --help to get help.
-t threads for connected.

Copy from reGeorg.
