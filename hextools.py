import struct

def hex_to_float(hex_input):
	return struct.unpack('!f', hex_input)[0]

