import socket
import time
import sys

"""get program arguments"""
myport = sys.argv[1]
parentIP = sys.argv[2]
parentPort = sys.argv[3]
ipsFileName = sys.argv[4]

"""create a new socket with UDP protocol and bind to given port"""
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
s.bind(('', int(myport)))

"""function for adding mappings in text file to given dictionary, by mapping domain to a string"""
def fileToMap(filename,map):
    with open(filename,"r") as f:
        for line in f:
            val = line.strip('\n')
            entr = val.split(',')[0]
            map[entr] = val

"""write mappings of given dictionary to given text file"""
def mapToFile(filename,map):
    with open(filename,"w") as f:
        for e in map.values():
            f.write(e+'\n')

"""function for learning mapping for given domain from parent server in case the server doesn't have it"""
def learn(domain,map,s):
    """send request to parent server for given domain"""
    s.sendto(domain.encode(), (parentIP,int(parentPort)))
    """save and decode recieved answer"""
    ans, pAddr = s.recvfrom(1024)
    match = ans.decode()
    l = match.split(',')
    """if there is no epoch-time field (meaning it's the first request for this domain)"""
    if len(l) == 3:
        """concat current epoch-time to string"""
        match += ',' + str(time.time())
    else:
        """update to current epoch-time"""
        l[3] = str(time.time())
        match = l[0]+','+l[1]+','+l[2]+','+l[3]
    """add new mapping to dictionary"""
    map[domain] = match
    return match


while True:
    map = {}
    """parse all data in ips file to map"""
    fileToMap(ipsFileName,map)
    """recieve request from client and decode data"""
    data, addr = s.recvfrom(1024)
    sData = data.decode()

    match = ""
    if sData in map:
        """if a match was found for requested domain then assign it to match"""
        match = map[sData]
        l = match.split(',')
        """if a epoch-time is written (meaning it's a dynamic mapping) check if TTL passed"""
        if len(l) == 4 and time.time() - float(l[3]) > float(l[2]):
            """remove existing mapping from dictionary and re-learn it from parent server"""
            map.pop(sData)
            if parentIP != "-1" and parentPort != "-1":
                match = learn(sData,map,s)
    elif parentIP != "-1" and parentPort != "-1":
        """if a match was not found and a parent server exists then learn it from it"""
        match = learn(sData,map,s)

    """send match back to client"""
    s.sendto(match.encode(), addr)

    """update file according to new mapping"""
    mapToFile(ipsFileName,map)