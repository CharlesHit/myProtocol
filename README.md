
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


## Data structure

- ACK – Indicates if packet is ACK or not. Valid values (1 or 0)
- SEQ – Sequence number of packet. Valid values (1 or 0)
- DATA – Application Data (8 bytes)
- CHKSUM – MD5 Checksum of packet (32 Bytes)

You will need to create the **packet**, load it with the necessary values and then send it to the server.

***This process will exactly mirror rdt 3.0 as shown in the textbook, so please make sure you follow it carefully!***

## How to do with cooruption functions 

Please see `UDP_Server.py, line 111`