import socket
import sys

"""get program arguments"""
sIp = sys.argv[1]
sPort = sys.argv[2]

"""create a new socket with UDP protocol"""
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    """ recieve and encode input of a domain from user"""
    req = input().encode()
    """send request to server for ip of given domain"""
    s.sendto(req, (sIp, int(sPort)))
    data, addr = s.recvfrom(1024)
    """parse recieved string to a list and get the ip"""
    ip = data.decode().split(',')[1]
    print(ip)