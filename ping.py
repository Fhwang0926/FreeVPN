#!/usr/bin/env python3
# https://gist.github.com/chidea/955cea841e5c76a7e5ee8aa02234409d
# http://dk0d.blogspot.kr/2016/07/code-for-sending-arp-request-with-raw.html
import time, datetime, socket, struct, select, random, asyncore, concurrent.futures
from multiprocessing import Process

# class PING(QThread):
class PING:


    def __init__(self):
        super().__init__()
        self.VERBOSE = False

        self.ICMP_ECHO_REQUEST = 8  # Seems to be the same on Solaris.
        self.ICMP_CODE = socket.getprotobyname('icmp')
        self.ERROR_DESCR = {
            1: ' - Note that ICMP messages can only be '
               'sent from processes running as root.',
            10013: ' - Note that ICMP messages can only be sent by'
                   ' users or processes with administrator rights.'
        }
        self.__all__ = ['chk_ttl', 'checksum', 'create_packet', 'ping', 'do_one', 'receive_ping' 'run_th_ping']

    def chk_ttl(self, ttl):
        try:
            mapping = {
                "255": "Stratus",
                "64": "Linux",
                "255": "Linux",
                "32": "Windows",
                "128": "Windows",
                "256": "Cisco",
            }
            rs = mapping[str(ttl)]
        except:
            rs = "????"
        return rs

    def checksum(self, source_string):
        sum = 0
        l = len(source_string)
        count_to = (l / 2) * 2
        count = 0
        while count < count_to:
            this_val = source_string[count + 1] * 256 + source_string[count]
            sum = sum + this_val
            sum = sum & 0xffffffff  # Necessary?
            count = count + 2
        if count_to < l:
            sum = sum + source_string[l - 1]
            sum = sum & 0xffffffff  # Necessary?
        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer


    def create_packet(self, id):
        header = struct.pack('bbHHh', self.ICMP_ECHO_REQUEST, 0, 0, id, 1)
        data = 192 * b'Q'
        my_checksum = self.checksum(header + data)
        header = struct.pack('bbHHh', self.ICMP_ECHO_REQUEST, 0,
                             socket.htons(my_checksum), id, 1)
        return header + data


    def do_one(self, dest_addr, timeout=1):
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.ICMP_CODE)
        except socket.error as e:
            if e.errno in self.ERROR_DESCR:
                # Operation not permitted
                raise socket.error(''.join((e.args[1], self.ERROR_DESCR[e.errno])))
            raise  # raise the original error
        try:
            host = socket.gethostbyname(dest_addr)
        except socket.gaierror:
            return
        # Maximum for an unsigned short int c object counts to 65535 so
        # we have to sure that our packet id is not greater than that.
        packet_id = int((id(timeout) * random.random()) % 65535)
        packet = self.create_packet(packet_id)
        while packet:
            # The icmp protocol does not use a port, but the function
            # below expects it, so we just give it a dummy port.
            sent = my_socket.sendto(packet, (dest_addr, 1))
            packet = packet[sent:]
        delay = self.receive_ping(my_socket, packet_id, time.time(), timeout)
        my_socket.close()
        return delay


    def receive_ping(self, my_socket, packet_id, time_sent, timeout):
        # Receive the ping from the socket.
        time_left = timeout
        while True:
            started_select = time.time()
            ready = select.select([my_socket], [], [], time_left)
            how_long_in_select = time.time() - started_select
            if ready[0] == []:  # Timeout
                return
            time_received = time.time()
            rec_packet, addr = my_socket.recvfrom(1024)
            icmp_ttl = rec_packet[22]
            icmp_header = rec_packet[20:28]
            type, code, checksum, p_id, sequence = struct.unpack(
                'bbHHh', icmp_header)
            if p_id == packet_id:
                return [icmp_ttl, time_received - time_sent]
            time_left -= time_received - time_sent
            if time_left <= 0:
                return


    def ping(self, dest_addr, timeout=3, count=1):
        avg = 0
        suc = 0

        for i in range(count):
            if self.VERBOSE: print('ping {}...'.format(dest_addr))

            result = self.do_one(dest_addr, timeout)
            if result != None:
                delay = result[1]
                ttl = result[0]
            else:
                delay = None
                ttl = None
            if delay == None:
                if self.VERBOSE: print('failed. (Timeout within {} seconds.)'.format(timeout))
            else:
                delay = round(delay * 1000.0, 4)
                avg += delay
                suc += 1
                print('{} - {} ms'.format(datetime.datetime.now(), delay))
        return (avg / suc) if avg else None


    def run_th_ping(self, target, loop=True, cycle=10):
        if not loop: self.ping(target); return
        while loop:
            self.ping(target)
            time.sleep(cycle)

if __name__ == '__main__':

    # Testing
    tmp = PING()
    tmp.VERBOSE = True
    proc = Process(target=tmp.run_th_ping, args=('8.8.8.8',))
    proc.start()
    proc.join()
    