import socket
import struct
import hashlib
import timeit

#####
# author Charles.M.H.
# 250995508
# Nov 20, 2019
#####

# address and port
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# time delay 9 ms
DELAY = 0.009


# Using signal handler is definitely a better idea but I dropped it
# For the sake of cross-platform
def signal_handler(signum, frame):
    raise Exception("Timed out!")


# By the first three data, calculate the check sum then send it
def rdt_builder(acknowledgement, sequence, message):
    # Build the UDP Packet
    values = (acknowledgement, sequence, message)
    #   by some format
    data_struct = struct.Struct('I I 8s')
    packed_data = data_struct.pack(*values)
    #   then calculate the check sum
    chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")
    values = (acknowledgement, sequence, message, chksum)
    # Build the final one
    pkt_struct = struct.Struct('I I 8s 32s')
    result_pkt = pkt_struct.pack(*values)
    # send it!
    return result_pkt


# check if a packet (already unpacked in tuple) has a ack == bit
def is_ack(pkt, bit):
    return pkt[0] == bit


# check if a packet (already unpacked in tuple) has a current check sum
def corrupt(pkt):
    # Build the UDP Packet and calculate the check sum
    values = (pkt[0], pkt[1], pkt[2])
    packer = struct.Struct('I I 8s')
    packed_data = packer.pack(*values)
    chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")
    # Compare check sums
    if pkt[3] == chksum:
        return False
    else:
        return True


# Send Data to the IP
def rdt_send(send_pkt):
    sock.sendto(send_pkt, (UDP_IP, UDP_PORT))


# Receive Data, with time check
#   Actually it is not a good idea, because I didn't really check the running time
#   But some package like timeit or signal, is platform bounded
#   So, I have to...
def rdt_receiver():
    # signal.signal(signal.SIGALRM, signal_handler)
    # signal.alarm(DELAY*1000)  # 9 mseconds

    # get the time receive a data
    t_start = timeit.default_timer()
    rcv_pkt = sock.recvfrom(1024)
    t_end = timeit.default_timer()

    # if time out, then throw an error
    if t_end - t_start > DELAY or rcv_pkt is None:
        raise Exception("Timed out!")

    # unpack the data and return it
    unpacker = struct.Struct('I I 8s 32s')
    data, addr = rcv_pkt  # buffer size is 1024 bytes
    received_pack = unpacker.unpack(data)
    return received_pack


# A toString printer
def print_pkt(pkt):
    print("ACK " + str(pkt[0]) + ";  SEQ " + str(pkt[1]) + ";  DATA " + str(pkt[2]) + ";  CHKSUM " + str(pkt[3]))


########################################################
# main function
########################################################

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP

# the message queue to be sent
msg_queue = [b'NCC-1701', b'NCC-1422', b'NCC-1017']

for message in msg_queue:
    # print("---->> New Turn:" + str(message))
    print("================================")
    # by default, the package will have seq = 0 in the beginning
    seq = 0
    #    ...also ack = 0 by default
    sent_packet = rdt_builder(0, seq, message)
    sent_tuple = (0, seq, message, None)  # this tuple is just a duplicated packet for printing info
    rdt_send(sent_packet)  # send it

    # print the sent message
    print("1 - Sent Package to server:\n    ", end="")
    print_pkt(sent_tuple)

    # received packet is the one from the server
    received_packet = None
    while received_packet is None:
        # Here the try statement is combined with the error throwing of rdt_receiver()
        try:
            received_packet = rdt_receiver()
            # if we received something, and not time out,
            #   and it is not corrupt, and the ack is correct,
            #   we will go to the next handshake
            if received_packet is not None and (corrupt(received_packet) is False and is_ack(received_packet, 0)):
                timer = False
            # Failed Case.
            # Either Data is corrupted,
            # or we received an empty package,
            #     which means the package is lost
            #
            # We have to Keep Waiting data from the Server
            #
            # Notice, if this error happened, we need to keep sending.
            # We must Stop this message
            if received_packet is not None and (corrupt(received_packet) or is_ack(received_packet, 1)):
                print("2 - Illegal msg received:\n    ", end="")
                print_pkt(received_packet)
                if corrupt(received_packet):
                    if received_packet[2] == b'\x00' * 8 and received_packet[3] == b'\x00' * 32 and received_packet[0] == received_packet[1] == 0:
                        print("WARNING: Lost ACK")
                    else:
                        print("WARNING: ACK corrupt")
                else:
                    print("  - ACK error")
                # all this three case, you need to resend
                print("================================")
                rdt_send(sent_packet)
                print("1 - Resent Package to server again:\n    ", end="")
                print_pkt(sent_tuple)
                received_packet = None
            # Success case. Print what we get, and move on
            if received_packet is not None:
                print("2 - Package Received from Server.\n    ", end="")
                print_pkt(received_packet)
        # Failed Case of Time Out. Keep Receiving
        except Exception:
            rdt_send(sent_packet)
            print("WARNING: Time Expired when wait for the server")
            print("================================")
            print("1 - Resent Package to server again:\n    ", end="")
            print_pkt(sent_tuple)
            received_packet = None

    # if received_packet is set as true, then we skip this message
    if received_packet is True:
        continue

    # Next step: the third and forth hand shaking
    # In the Client side, it is our duty
    #   to update the ACK, mode by 2
    # and keep seq as it is
    ack = (received_packet[0] + 1) % 2
    seq = received_packet[1]
    sent_packet = rdt_builder(ack, seq, message)
    sent_tuple = (ack, seq, message, received_packet[3])
    rdt_send(sent_packet)
    print("3 - Sent Package to server:\n    ", end="")
    print_pkt(sent_tuple)

    # Mirror Story above
    received_packet = None
    while received_packet is None:
        try:
            received_packet = rdt_receiver()
            # Success Case
            if received_packet is not None and (corrupt(received_packet) is False and is_ack(received_packet, 1)):
                timer = False
            # Failed Case. Corrupt. Keep Receiving
            if received_packet is not None and (corrupt(received_packet) or is_ack(received_packet, 0)):
                print(received_packet is not None)
                print(is_ack(received_packet, 0))
                print("4 - Illegal msg receive+d: " + str(message) + "\n    ", end="")
                if corrupt(received_packet):
                    if received_packet[2] == b'\x00' * 8 and received_packet[3] == b'\x00' * 32 and received_packet[0] == received_packet[1] == 0:
                        print("WARNING: Lost ACK")
                    else:
                        print("WARNING: ACK corrupt")
                else:
                    print_pkt("WARNING: ACK error")
                print("================================")
                # all this three case, you need to resend
                rdt_send(sent_packet)
                print("1 - Resent Package to server again:\n    ", end="")
                print_pkt(sent_tuple)
                received_packet = None
            if received_packet is not None:
                print("4 - Package Received from Server.\n    ", end="")
                print_pkt(received_packet)
                print("Data Exchange Completed!")
                print("================================")
        # Failed Case. Time Out. Keep Receiving
        except Exception:
            rdt_send(sent_packet)
            print("WARNING: Time Expired when wait for server")
            print("3 - Resent Package to server again:\n    ", end="")
            print_pkt(sent_tuple)
