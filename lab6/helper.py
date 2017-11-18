from check import ip_checksum

def make_packet(seq_num, message):
	"""
	Creates a packet using the sequence number and data provided. 
	Calculates checksum of data add concatenates it with data.
	Returns a single string containing sequence number, data, and
	checksum, in that order.
	"""
	tmp = str(seq_num) + message
	checksum = ip_checksum(tmp)
	final_packet = tmp + checksum
	return final_packet

def corrupt(packet):
	"""
	Checks if packet was corrupted during transmission. Calculates
	checksum and compares it to the one included in the packet.
	Returns true if data is corrupted, false otherwise.
	"""
	data = packet[:len(packet) - 2]
	checksum = packet[len(packet) - 2:]
	calculated_check = ip_checksum(data)
	if checksum != calculated_check:
		return True
	return False

def isACK(packet, expected_ack):
	"""
	Checks if packet contains correct ACK number. Returns True
	if it contains the correct ACK, false otherwise.
	"""
	packet_ack = int(packet[0])
	if packet_ack != expected_ack:
		return False
	return True

