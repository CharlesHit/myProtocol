import socket
import struct
import hashlib
import timeit
import signal
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

DELAY = 0.009


def signal_handler(signum, frame):
    raise Exception("Timed out!")


# organize data
def rdt_builder(ack, seq, msg):
    # Build the UDP Packet
    values = (ack, seq, msg)
    data_struct = struct.Struct('I I 8s')
    packed_data = data_struct.pack(*values)
    chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")
    values = (ack, seq, msg, chksum)
    pkt_struct = struct.Struct('I I 8s 32s')
    result_pkt = pkt_struct.pack(*values)
    return result_pkt


def is_ack(pkt, bit):
    return pkt[0] == bit


def corrupt(pkt):
    #unpacker = struct.Struct('I I 8s 32s')
    # unpacked_pkt = unpacker.unpack(pkt)
    # Create the Checksum for comparison
    values = (pkt[0], pkt[1], pkt[2])
    packer = struct.Struct('I I 8s')
    packed_data = packer.pack(*values)
    chksum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")
    # Compare chksum to test for corrupt data
    if pkt[3] == chksum:
        return False
    else:
        return True


# Send Data
def rdt_send(send_pkt):
    sock.sendto(send_pkt, (UDP_IP, UDP_PORT))


# Receive Data
def rdt_receiver():
    # signal.signal(signal.SIGALRM, signal_handler)
    # signal.alarm(DELAY*1000)  # 9 mseconds

    t_start = timeit.default_timer()

    rcv_pkt = sock.recvfrom(1024)

    t_end = timeit.default_timer()

    if t_end - t_start > DELAY or rcv_pkt is None:
        raise Exception("Timed out!")

    unpacker = struct.Struct('I I 8s 32s')
    data, addr = rcv_pkt  # buffer size is 1024 bytes
    received_pack = unpacker.unpack(data)
    return received_pack


def print_pkt(pkt):
    print("ACK " + str(pkt[0]) + ";  SEQ " + str(pkt[1]) + ";  DATA " + str(pkt[2]) + ";  CHKSUM " + str(pkt[3]))


def output(pkt, sent_pkt, start_time, timer_opened):
    # Received Packet (with all packet values shown)
    print("====================")
    print("Received: ", end='')
    print_pkt(pkt)
    # Packet Checksum Compare Result (ie. Corrupt or not corrupt)
    if corrupt(rcvpkt):
        print("corrupt")
    else:
        print("not corrupt")
    # Sent Packet (with all packet values shown)
    print("Sent Package: ", end='')
    print_pkt(sent_pkt)
    # Timer Expired
    end_time = timeit.default_timer()
    if start_time - end_time > DELAY and timer_opened is True:
        print("time expired")
    else:
        print("time not expired")
    print("====================")


print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)

# Send the UDP Packet
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP

msg_to_be_sent = [b'NCC-1701', b'NCC-1422', b'NCC-1017']

for message in msg_to_be_sent:
    # print("New Turn")
    # 0.0
    sndpkt = rdt_builder(0, 0, message)
    snd_tuple = (0, 0, message, None)

    rdt_send(sndpkt)
    # print("sent, 1")

    start = timeit.default_timer()
    timer = True

    # 0.1
    # print("0.1")

    try:
        rcvpkt = rdt_receiver()
        # 0.2
        if rcvpkt is not None and (corrupt(rcvpkt) or is_ack(rcvpkt, 1)):
            print("illegal msg: " + str(message), end="")
            if(corrupt(rcvpkt)):
                print_pkt(": corrupt")
            else:
                print_pkt(": ack error")
            # output(rcvpkt, snd_tuple, start, timer)
        if rcvpkt is not None and (corrupt(rcvpkt) is False and is_ack(rcvpkt, 0)):
            timer = False
        if rcvpkt is not None:
            print("Package Received from Server. ", end="")
            print_pkt(rcvpkt)
    except Exception:
        if timer is True:
            rdt_send(sndpkt)
            print("Time Expired, resent: " + str(message))
            start = timeit.default_timer()
            continue

    # 1.0
    # print("1.0")
    sndpkt = rdt_builder(0, 1, message)
    snd_tuple = (0, 1, message, rcvpkt[3])
    rdt_send(sndpkt)
    # print("sent, 2")

    start = timeit.default_timer()
    timer = True

    # 1.1
    # print("1.1")
    stop = timeit.default_timer()
    try:
        rcvpkt = rdt_receiver()
        # 0.2
        if rcvpkt is not None and (corrupt(rcvpkt) or is_ack(rcvpkt, 0)):
            # output(rcvpkt, snd_tuple, start, timer)
            print("illegal msg: " + str(message), end="")
            if (corrupt(rcvpkt)):
                print_pkt(": corrupt")
            else:
                print_pkt(": ack error")
        if rcvpkt is not None and (corrupt(rcvpkt) is False and is_ack(rcvpkt, 1)):
            timer = False
        if rcvpkt is not None:
            # output(rcvpkt, snd_tuple, start, timer)
            print("Package Received from Server. ", end="")
            print_pkt(rcvpkt)
    except Exception:
        if timer is True:
            print("Time Expired, resent: " + str(message))
            rdt_send(sndpkt)
            start = timeit.default_timer()
