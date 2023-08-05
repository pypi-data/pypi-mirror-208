import sys, math, random
from typing import Callable, Any
from abc import ABC, abstractmethod
from scapy.plist import SndRcvList, PacketList
from scapy.all import IP, UDP, ICMP, Raw, sr1
from traceroute.lorem import lorem


_WINTRACEROUTE_PRINT_FILE = sys.stdout
_WINTRACEROUTE_IP_ID = 42

def trace(host:str,
          IP_PACKET_SUPPLIER=Callable[[str,str,int],Any],
          DATAGRAM_SUPPLIER=Callable[[int],Any],
          min_ttl:int=1,
          max_ttl:int=30,
          num_per_fleet:int=3,
          timeout:int=5,
          port:int=33434,
          source:str=None):
    # for pretty printing
    f_log10_maxttl = int(math.log10(max_ttl) + 1)
    f_ttl_str_format = '{:'+str(f_log10_maxttl)+'d}'
    f_log10_timeout = int(math.log10(timeout*1000) + 1)
    f_time_str_width = f_log10_timeout+4
    f_time_str_format = '{:'+str(f_time_str_width)+'.3f}'
    # now lets go tracerouting
    responses = list()
    times = list()
    dest_reached = False
    for ttl in range(min_ttl, max_ttl+1):
        # this is for each ttl
        ttl_responses = list()
        ttl_times = list()
        # print ttl index
        print(' ', f_ttl_str_format.format(ttl), "\t",  sep='', end='', \
                file=_WINTRACEROUTE_PRINT_FILE)
        for _ in range(num_per_fleet):
            # this is for each packet in the fleet (3 by default)
            packet = IP_PACKET_SUPPLIER(host, source, ttl) / \
                     DATAGRAM_SUPPLIER(port)
            response = sr1(packet, timeout=timeout, verbose=False)
            if response:
                ttl_responses.append(response)
                time = (response.time * 1000) - (packet.sent_time * 1000)
                ttl_times.append(time)
            else:
                ttl_responses.append(None)
                ttl_times.append(None)
            #print(" ###", response)
        # append this ttl's data to the record
        responses.append(ttl_responses)
        times.append(ttl_times)
        # print results
        summarize_ttl(ttl_responses, ttl_times,
                      restlines_pfx=(' '*(f_log10_maxttl+1))+'\t',
                      time_str_format=f_time_str_format,
                      time_str_width=f_time_str_width)
        # terminate if destination reached
        if is_dest_reached(ttl_responses, dest=host):
            dest_reached = True
            break
    # end of run -- maybe destination reached, maybe not.
    summarize_termination(host, ttl_times, ttl, dest_reached=dest_reached)

    # return the records
    return (responses, times)

def trace_udp(host:str,
              udp_length=2,
              min_ttl:int=1,
              max_ttl:int=30,
              num_per_fleet:int=3,
              timeout:int=5,
              port:int=33434,
              udp_content:str='asc',
              source:str=None,
              ip_id_variation:bool=True):
    
    change_ip_id(True)
    
    ip_packet_supplier = \
        lambda host, source, ttl: \
            make_ip_packet(host=host, source=source, 
                           ttl=ttl, ip_id_variation=ip_id_variation)
    datagram_supplier = \
        lambda port: \
            make_udp_packet(port=port) / get_junk(udp_length, kind=udp_content)
    trace(host, ip_packet_supplier, datagram_supplier,
          min_ttl=min_ttl, max_ttl=max_ttl, num_per_fleet=num_per_fleet,
          timeout=timeout, port=port, source=source)

def trace_icmp(host:str,
               min_ttl:int=1,
               max_ttl:int=30,
               num_per_fleet:int=3,
               timeout:int=5,
               port:int=33434,
               source:str=None,
               ip_id_variation:bool=True):
    
    change_ip_id(True)
        
    ip_packet_supplier = \
        lambda host, source, ttl: \
            make_ip_packet(host=host, source=source, 
                           ttl=ttl, ip_id_variation=ip_id_variation)
    datagram_supplier = \
        lambda port: \
            make_icmp_packet()  # ignore port on icmp
    trace(host, ip_packet_supplier, datagram_supplier,
          min_ttl=min_ttl, max_ttl=max_ttl, num_per_fleet=num_per_fleet,
          timeout=timeout, port=port, source=source)


def summarize_ttl(responses:list, times:list,
                  firstline_pfx:str='', restlines_pfx:str='',
                  time_str_format:str='%8.3f',
                  time_str_width:int=8):
    assert len(responses) == len(times)
    # build sorted list
    fleetsize = len(responses)
    # sort by host
    sorted_responses = dict()  # map host -> list of indices
    for i in range(0, len(responses)):
        response = responses[i]
        response_source = response.src if response else ' (no response) '
        if response_source in sorted_responses.keys():
            sorted_responses[response_source].append(i)
        else:
            sorted_responses[response_source] = [i]
    # now print results
    is_first_line = True
    for host in sorted_responses.keys():
        if is_first_line:
            print(firstline_pfx, end='', file=_WINTRACEROUTE_PRINT_FILE)
        else:
            print(restlines_pfx, end='', file=_WINTRACEROUTE_PRINT_FILE)
        indices = sorted_responses[host]
        for i in range(0, fleetsize):
            if i in indices:
                time = times[i]
                if time == None:
                    print(' '*(time_str_width-4) + '*   ' + '\t', end='', 
                          file=_WINTRACEROUTE_PRINT_FILE)
                else:
                    print(time_str_format.format(time) + '\t', end='', 
                          file=_WINTRACEROUTE_PRINT_FILE)
            else:
                print(' '*time_str_width + '\t', end='', 
                      file=_WINTRACEROUTE_PRINT_FILE)
        print(host, file=_WINTRACEROUTE_PRINT_FILE)
        is_first_line = False

def is_dest_reached(responses:list, dest):
    for rt in responses:
        if rt == None:
            continue
        else:
            rt_icmp = rt[ICMP]
            if rt_icmp.type == 3 or rt.src == dest:
                return True  # Dest unreachable, port unavailable
    return False

def summarize_termination(host, times, ttl, dest_reached):
    print(file=_WINTRACEROUTE_PRINT_FILE)
    if dest_reached:
        print("Destination '" + host + "' reached " + \
            " in RTT " + summarize_times(times, as_string=True) + " ms " + \
            " via " + str(ttl) + " hops.", \
            file=_WINTRACEROUTE_PRINT_FILE)
    else:
        print("Maximum TTL reached, but no '" + host + "' in sight. Aborting.", \
            file=_WINTRACEROUTE_PRINT_FILE)
        print("If you wish to continue the search, consider increasing the `--maxttl`\n" + \
            "  setting on the next try. Besides that, try a different `--module`, maybe?", \
            file=_WINTRACEROUTE_PRINT_FILE)

def summarize_times(times:list,
                    as_string:bool=False):
    min = times[0]
    max = times[0]
    sum = times[0]

    if len(times) > 1:
        for t in times[1:]:
            if t < min:
                min = t
            if t > max:
                max = t
            sum += t

    avg = sum / len(times)

    if as_string:
        return "min. %.3f, avg. %.3f, max. %.3f" % (min, avg, max)
    else:
        return (min, avg, max)


def make_ip_packet(host:str, source:str, ttl:int, ip_id_variation:bool):
    if ip_id_variation:
        change_ip_id()
    if source != None:
        packet = IP(id=_WINTRACEROUTE_IP_ID, 
                    dst=host, 
                    src=source, 
                    ttl=ttl)
    else:
        packet = IP(id=_WINTRACEROUTE_IP_ID,
                    dst=host, 
                    ttl=ttl)
    return packet

def make_udp_packet(port:int):
    return UDP(dport=port)

def make_icmp_packet():
    return ICMP(type=8)
    #return ICMP()
    

def change_ip_id(first_time:bool=False):
    global _WINTRACEROUTE_IP_ID
    if first_time:
        random.seed()
    # the IP Identification field is 16 bits
    _WINTRACEROUTE_IP_ID = random.randint(0, 2**16-1)


def get_junk(length=2, kind='42'):
    if kind == '42':
        ret = b"42" * int(length/2)
        if length%2 != 0:
            ret += "!"
        return ret
    elif kind == 'zeros':
        return Raw(b"\x00"*length)
    elif kind == '00':
        return b"0"*length
    elif kind == 'loremipsum':
        return lorem[0:length]
    elif kind == 'asc':
        byts = bytes([n%256 for n in range(length)])
        return Raw(byts)
    else:
        junk_msg = 'invalid kind of junk! '
        junk_msg_infl = junk_msg * (int(length / 20) + 1)
        return junk_msg_infl[0:length]
