import socket
import sys
import time
from check import ip_checksum
from threading import Timer, Lock
from helper import make_packet, corrupt, isACK
from message import messages
from collections import deque
import copy

host = 'localhost'
port = 8888

buff_lock = Lock()
print_lock = Lock()
def timeout(s, packet):
	print_lock.acquire()
	print 'Timeout. Resending n packets...'
	print '\n'
	global sentbuffer
	# buffcopy = copy.copy(sentbuffer)
	buff_lock.acquire()
	for message in sentbuffer:
		print '\tResending...'
		print '\tSEQ: ' + message[0]
		print '\tMessage: ' + message[1:len(message)-2]
		print '\n'
		s.sendto(message, (host, port))
	buff_lock.release()
	global t
	t = Timer(1.0, timeout, [s, packet])
	t.start()
	print_lock.release()

base = 0 # base of the window
nextseqnum = 0 # next available sequence number
n = 4 # Window size
sentbuffer = deque([]) # store the packets that were sent but have not been ACKed
messagecount = 0
# Creating UDP socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

while 1: # Execute while there are still unsent messages
	while messages and (nextseqnum < base + n):
		message = messages.popleft()
		send_packet = make_packet(nextseqnum, message);
		buff_lock.acquire()
		sentbuffer.append(send_packet)
		buff_lock.release()
		print_lock.acquire()
		print 'Sending...'
		print 'SEQ: ' + str(nextseqnum)
		print 'MESSAGE: ' + message
		print '\n'
		print_lock.release()

		if messagecount == 5:
			send_packet = send_packet + 'a'

		try:
			s.sendto(send_packet, (host, port))

		except socket.error, msg:
			print 'Error code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()

		messagecount += 1
		# Packet should have either been sent or program ended by this point.
		if base == nextseqnum:
			t = Timer(1.0, timeout, [s, sentbuffer[0]])
			t.start()

		nextseqnum += 1

	
	# n packets should be in transit by now.
	# Time to listen for ACKs
	d = s.recvfrom(1024)
	data = d[0]

	if not corrupt(data) and isACK(data, base):
		# Correct ACK received
		print_lock.acquire()
		print 'Receiving...'
		print 'ACK: ' + data[0]
		print 'REPLY: ' + data[1:len(data)-2]
		print '\n'
		print_lock.release()
		base += 1

		buff_lock.acquire()
		sentbuffer.popleft()
		buff_lock.release()
		if base == nextseqnum:
			time.sleep(.1)
			t.cancel()
		else:
			time.sleep(.1)
			t.cancel()
			t = Timer(1.0, timeout, [s, sentbuffer[0]])
			t.start()

	if not sentbuffer and not messages:
		print 'All messages sent.'
		print '\n'
		break
