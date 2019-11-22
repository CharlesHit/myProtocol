
# Assignment 3

## Intro: theory

(S = sender, R = receiver)

### Base case:

S: sent
    
R: got

### Advanced Case: with illegal msg
    
S: blabla
    
R: What? - Use the checksum to find the illegal of msg and set ACK = 1(acknowledgement) then send back
    
S: send again, with SEQ = bit changed (sequence number)

R: return
    
### Advanced Case 2: with pkg lost

S: blabla

S: No response? Resend

    

## Intro: what he already done

Part of the s/c are already made, and the data structure, including:

- Create a UDP connection
- Create a ‘pseudo UDP packet’
- Calculate the checksum
- Fill the packet and send it to the server
- Receive the packet and unpack it
- Compare checksums to ensure the packet is not corrupted


### Data structure

- ACK – Indicates if packet is ACK or not. Valid values (1 or 0)
- SEQ – Sequence number of packet. Valid values (1 or 0)
- DATA – Application Data (8 bytes)
- CHKSUM – MD5 Checksum of packet (32 Bytes)

You will need to create the **packet**, load it with the necessary values and then send it to the server.

***This process will exactly mirror rdt 3.0 as shown in the textbook, so please make sure you follow it carefully!***

## Part A

Run your Client and Server Applications and capture the exchange of information between them, you must submit two screenshots for this part.

### ALGORITHMS for sender

#### send - senario 1 - ACK
```
- make: [0, data, checksum]
- send
- start timer

receive:

if(corrupt || isACK(1)):
    do nothing

if timeout:
    udt_send(same package)
    start_timer

receive:

if(notcorrupt && isACK(0)):
    stop timer

```

#### send - senario 2

```

- make: [1, data, checksum]
- send
- start timer

receive:

if(corrupt || isACK(0)):
    do nothing
else:
    do nothing

if timeout:
    udt_send(next package)
    start_timer

receive:

if(notcorrupt && isACK(1)):
    stop timer
else:
    do nothing
```    

### ALGORITHMS for receiver

```
if received:    
    if(not corrupt && seq == 0)
        send(ACK, 0, checksum)
    if(corrupt || seq == 0)
        send(ACK, 0, checksum)

if received:    
    if(not corrupt && seq == 1)
        send(ACK, 1, checksum)
    if(corrupt || seq == 1)
        send(ACK, 1, checksum)      

```

### UDP_Client

This app must connect to the UDP_Server app via UDP (you must use the local loopback address of $127.0.0.1$ but please choose any port number you wish) then send three separate packets containing the following information:

- NCC-1701
- NCC-1422
- NCC-1017

### UDP_Server

This app will establish a UDP socket and listen for incoming connections from the client. When a connection is made the server will consume the data and follow the ***rdt 2.2*** process as shown in chapter 3 of the course textbook.

Remember, in order to accomplish this, the server application must also be able to send acknowledgements because we will be using the rdt 2.2 process for creating a reliable transfer over UDP. 

The output from the UDP_Server and UDP_Client should display a line of text for each of the following actions:

- Received Packet (with all packet values shown)
- Packet Checksum Compare Result (ie. Corrupt or not corrupt)
- Sent Packet (with all packet values shown)
- Timer Expired

## Part 2

You will be ***delaying*** server ACKs, ***corrupting*** server ACKs, and ***losing Server*** ACKs to simulate an unreliable channel. Once you have implemented these functions you will need to run your applications and show an exchange that demonstrates all three conditions (Corruption, Delay, and Loss) by submitting two screenshots (one of the Client side and one of the Server side). 