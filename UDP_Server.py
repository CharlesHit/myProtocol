import socket
import struct
import time
import random
import hashlib

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
unpacker = struct.Struct('I I 8s 32s')


# organize data
def rdt_builder(ack, seq, pkt, check_sum):
    # Build the UDP Packet
    msg = pkt
    # values = (ack, seq, msg)
    # data_struct = struct.Struct('I I 8s')
    # packed_pkt = data_struct.pack(*values)
    # check_sum = bytes(hashlib.md5(packed_pkt).hexdigest(), encoding="UTF-8")
    values = (ack, seq, msg, check_sum)
    pkt_struct = struct.Struct('I I 8s 32s')
    result_pkt = pkt_struct.pack(*values)
    return result_pkt


def is_ack(pkt, bit):
    return pkt[0] == bit


def has_seq(pkt, bit):
    return pkt[1] == bit


def rdt_send(send_pkt, remote_address):
    sock.sendto(send_pkt, (UDP_IP, remote_address))


def set_ack(pkt_value):
    packed_data_arr = bytearray(pkt_value)
    packed_data_arr[3] = 1
    return bytes(packed_data_arr)


def set_seq(pkt_value):
    packed_data_arr = bytearray(pkt_value)
    packed_data_arr[7] = 1
    return bytes(packed_data_arr)


def network_delay():
    if True and random.choice([0,1,0]) == 1:  # Set to False to disable Network Delay. Default is 33% packets are delayed
        time.sleep(.01)
        print("Packet Delayed")
    else:
        print("Packet Sent")


def network_loss():
    if True and random.choice([0,1,1,0]) == 1:  # Set to False to disable Network Loss. Default is 50% packets are lost
        print("Packet Lost")
        return 1
    else:
        return 0


def packet_checksum_corrupter(packetdata):
    error_msg = b'Corrupt!'
    if True and random.choice([0,1,0,1]) == 1:  # Set to False to disable Packet Corruption. Default is 50% packets are corrupt
        return error_msg
    else:
        return packetdata


def get_check_sum(pkt):
    # Create the Checksum for comparison
    packet_pkt = unpacker.unpack(pkt)
    values_pkt = (packet_pkt[0], packet_pkt[1], packet_pkt[2])
    packer_pkt = struct.Struct('I I 8s')
    packed_pkt = packer_pkt.pack(*values_pkt)
    check_sum = bytes(hashlib.md5(packed_pkt).hexdigest(), encoding="UTF-8")
    return check_sum


def calculate_check_sum(ack, seq, msg):
    values_pkt = (ack, seq, msg)
    packer_pkt = struct.Struct('I I 8s')
    packed_pkt = packer_pkt.pack(*values_pkt)
    check_sum = bytes(hashlib.md5(packed_pkt).hexdigest(), encoding="UTF-8")
    return check_sum



# Create the socket and listen
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    # 1
    # Receive Data
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    UDP_Packet = unpacker.unpack(data)
    print("1 - received from:", addr)
    print("received message:", UDP_Packet)

    # Compare check sums to test for corrupt data
    chksum = get_check_sum(data)
    if UDP_Packet[3] == chksum and has_seq(UDP_Packet, 0):
        print('CheckSums Match, Packet OK')
        rdt_send(rdt_builder((UDP_Packet[0])%2, 0, UDP_Packet[2],
                             calculate_check_sum((UDP_Packet[0])%2, 0, UDP_Packet[2])), addr[1])
        network_delay()
        print("sent 1-1")
    else:
        if UDP_Packet[3] != chksum or has_seq(UDP_Packet, 0):
            print('CheckSums Do Not Match, Packet Corrupt')
            rdt_send(rdt_builder((UDP_Packet[0]) % 2, 0, UDP_Packet[2],
                                 calculate_check_sum((UDP_Packet[0]) % 2, 0, UDP_Packet[2])), addr[1])
        print("sent 1-2")

    # 2
    # Receive Data
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    UDP_Packet = unpacker.unpack(data)
    print("2 - received from:", addr)
    print("received message:", UDP_Packet)

    # Compare check sums to test for corrupt data
    chksum = get_check_sum(data)
    print(UDP_Packet)
    if UDP_Packet[3] == chksum and has_seq(UDP_Packet, 1):
        print('2 - CheckSums Match, Packet OK')
        rdt_send(rdt_builder((UDP_Packet[0]+1)%2, 1, UDP_Packet[2], calculate_check_sum((UDP_Packet[0]+1)%2, 1, UDP_Packet[2])), addr[1])
        print("sent 2-1")
    else:
        # if UDP_Packet[3] != chksum or has_seq(UDP_Packet, 1):
        print('2 - CheckSums Do Not Match, Packet Corrupt')
        rdt_send(rdt_builder((UDP_Packet[0]+1)%2, 1, UDP_Packet[2], calculate_check_sum((UDP_Packet[0]+1)%2, 1, UDP_Packet[2])), addr[1])
        print("sent 2-2")
