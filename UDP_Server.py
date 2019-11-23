import socket
import struct
import time
import random
import hashlib

#####
# author Charles.M.H.
# 250995508
# Nov 20, 2019
#####

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
unpacker = struct.Struct('I I 8s 32s')


# By the first three data, calculate the check sum then send it
#   Slight different by the Client's version
def rdt_builder(acknowledgement, sequence, message, check_sum):
    # Build the UDP Packet
    values = (acknowledgement, sequence, message, check_sum)
    pkt_struct = struct.Struct('I I 8s 32s')
    result_pkt = pkt_struct.pack(*values)
    # send it!
    return result_pkt


def is_ack(pkt, bit):
    return pkt[0] == bit


def has_seq(pkt, bit):
    return pkt[1] == bit


def rdt_send(send_pkt, remote_address):
    sock.sendto(send_pkt, (UDP_IP, remote_address))


# the function generate the transaction delay
def network_delay():
    if True and random.choice(
            [0, 0, 0, 0, 1, 0]) == 1:  # Set to False to disable Network Delay. Default is 33% packets are delayed
        time.sleep(.01)
        print("    Packet Delayed")
        return True
    else:
        print("    Packet Sent")
        return False


def network_loss():
    if True and random.choice(
            [0, 0, 0, 0, 1, 0]) == 1:  # Set to False to disable Network Loss. Default is 50% packets are lost
        print("Packet Lost")
        return True
    else:
        return False


def packet_checksum_corrupter():
    error_msg = b'Corrupt!'
    if True and random.choice(
            [0, 0, 0, 0, 1, 0]) == 1:  # Set to False to disable Packet Corruption. Default is 50% packets are corrupt
        print("Data Corrupt")
        return True
    else:
        return False


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
    # the indicator to control the artificial error
    no_error_happened = True
    while no_error_happened is True:
        print("================================")
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        UDP_Packet = unpacker.unpack(data)
        print("1 - received from:", addr)
        print("    received message:", UDP_Packet)
        # Compare check sums to test for corrupt data
        chksum = get_check_sum(data)
        # if it is corrupt
        if UDP_Packet[3] == chksum and has_seq(UDP_Packet, 0):
            print('1 - CheckSums matched, packet OK')
            print("    1 - sent package back to client")

            ########################################
            # Choose either Delays, Loss or Checksum_Corrupter
            ########################################

            ########################################
            # 0. peace
            # Remain and only remain this part, the server will run without any corrupt
            # no_error_happened = False
            ########################################

            ########################################
            # 1. Delays
            # if you wanna make a delay, comment the second line; otherwise the first
            # 1
            no_error_happened = network_delay()
            # 2
            # no_error_happened = False
            ########################################

            ########################################
            # 2. Loss
            # if you wanna make a loss, set the part 3 all uncomment,
            #   then comment the second line; otherwise comment the first
            # 1
            no_error_happened = network_loss()
            # 2
            # no_error_happened = False
            #
            # 3
            if no_error_happened is True:
                rdt_send(rdt_builder(0, 0, b'', b''), addr[1])
                continue
            ########################################

            ########################################
            # 3. checksum_corrupter
            # if you wanna make a checksum corrupter, set the part 3 all uncomment,
            #   then comment the second line; otherwise comment the first
            # 1
            no_error_happened = packet_checksum_corrupter()
            # 2
            # no_error_happened = False
            # 3
            if no_error_happened is True:
                ERROR_SEQ = 512
                ERROR_MSG = b'Corrupt!'
                rdt_send(rdt_builder(UDP_Packet[0], UDP_Packet[1], UDP_Packet[2],
                                     calculate_check_sum(UDP_Packet[0], ERROR_SEQ, ERROR_MSG)), addr[1])
                continue
            ########################################

            # the sender will keep the ACK as it is
            #   while change the SEQ
            seq = (UDP_Packet[1] + 1) % 2
            rdt_send(rdt_builder(UDP_Packet[0], seq, UDP_Packet[2],
                                 calculate_check_sum(UDP_Packet[0], seq, UDP_Packet[2])), addr[1])
        else:
            # if it corrupt, there is two scenarios:
            #
            # 1. the check sum error
            #
            # 2. the sequential error
            if UDP_Packet[3] != chksum or has_seq(UDP_Packet, 0):
                print('1 - CheckSums failed to match, Packet Corrupt')
                print("    2 - sent package back to client:", UDP_Packet)
                seq = (UDP_Packet[1] + 1) % 2
                rdt_send(rdt_builder(UDP_Packet[0], seq, UDP_Packet[2],
                                     calculate_check_sum(UDP_Packet[0], seq, UDP_Packet[2])), addr[1])
            else:
                print("It is illegal to have the SEQ = %d.\nDropped" % (UDP_Packet[1]))

                # keep in mind, in sequential error, we have to update both seq and ack
                seq = (UDP_Packet[1] + 1) % 2
                ERROR_SEQ = 100
                ack = (UDP_Packet[0] + 1) % 2
                rdt_send(rdt_builder(ack, seq, UDP_Packet[2],
                                     calculate_check_sum(ack, ERROR_SEQ, UDP_Packet[2])), addr[1])
                delayed = True

    # 2 - almost the same. Only has_seq(UDP_Packet, 1) is different
    # Receive Data
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    UDP_Packet = unpacker.unpack(data)
    print("2 - received from:", addr)
    print("    received message:", UDP_Packet)

    # Compare check sums to test for corrupt data
    chksum = get_check_sum(data)
    if UDP_Packet[3] == chksum and has_seq(UDP_Packet, 1):
        print('2 - CheckSums Match, Packet OK')
        # Sent
        print("    2 - sent package back to client:", UDP_Packet)
        # the sender will keep the ACK as it is while change the SEQ
        seq = (UDP_Packet[1] + 1) % 2
        rdt_send(rdt_builder(UDP_Packet[0], seq, UDP_Packet[2], calculate_check_sum(UDP_Packet[0], seq, UDP_Packet[2])),
                 addr[1])
    else:
        if UDP_Packet[3] != chksum or has_seq(UDP_Packet, 1):
            # if UDP_Packet[3] != chksum or has_seq(UDP_Packet, 1):
            print('2 - CheckSums Do Not Match, Packet Corrupt')
            seq = (UDP_Packet[1] + 1) % 2
            rdt_send(
                rdt_builder(UDP_Packet[0], seq, UDP_Packet[2], calculate_check_sum(UDP_Packet[0], seq, UDP_Packet[2])),
                addr[1])
            print("    2 - sent package back to client")
        else:
            print("It is illegal to have the SEQ = %d.\nDropped" % (UDP_Packet[1]))
            seq = (UDP_Packet[1] + 1) % 2
            ERROR_SEQ = 100
            ack = (UDP_Packet[0] + 1) % 2
            rdt_send(rdt_builder(ack, seq, UDP_Packet[2],
                                 calculate_check_sum(ack, ERROR_SEQ, UDP_Packet[2])), addr[1])
            delayed = True
