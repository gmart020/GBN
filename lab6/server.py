import socket
import sys
from check import ip_checksum
from helper import make_packet, corrupt, isACK
from time import sleep

HOST = ''
PORT = 8888

expectedseqnum = 0

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg:
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

reply = "" 

while 1:
	d = s.recvfrom(1024)
	data = d[0]
	addr = d[1]

	if not data:
		break
	
	seq = data[0]
	message = data[1:len(data) - 2]
	checksum = data[len(data) - 2:]
	reply = 'OK...' + message

	if not corrupt(data):
		if isACK(data, expectedseqnum):
			print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + '(SEQ: ' + str(seq) + ') '  + message.strip()
			print '\n'
			packet = make_packet(expectedseqnum, reply)
			s.sendto(packet, addr)
			expectedseqnum += 1	

		else:
			print 'Packet ' + seq  + ' received out of order. Deleting ...'
			print 'Sending ACK ' + str(expectedseqnum - 1)
			print '\n'
			packet = make_packet(expectedseqnum - 1, reply)
			s.sendto(packet, addr)
			del data		

	else:
		print 'Packet ' + seq  + ' is corrupted. Deleting ...'
		print 'Sending ACK ' + str(expectedseqnum - 1)
		print '\n'
		packet = make_packet(expectedseqnum - 1, reply)
		s.sendto(packet, addr)
		del data		

s.close()
