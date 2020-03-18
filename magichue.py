#!/usr/bin/python3

import sys
import socket
from argparse import ArgumentParser

def add_checksum(values):
    checksum = int(hex(sum(values) & 0xff), 16)
    values.append(checksum)
    return values

def get_version(ip):
    try: 
        data = bytearray(process_raw('48:46:2d:41:31:31:41:53:53:49:53:54:48:52:45:41:44')) #HF-A11ASSISTHREAD
        
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        s.sendto(data, (ip,48899))
        response = s.recvfrom(1024)
        
        msg = response[0].decode('utf-8')
        version = msg.split(',')
        
        return version[2]
    except:
        print_error("Could not get the bulb's version")
        return None

def send(ip, values):
    try:
        get_version(ip)

        s = socket.socket()
        s.connect((ip, 5577))
        s.send(bytearray(add_checksum(values)))
        s.close()
    except:
        print_error("Could not send the message to the bulb")

def process_raw(raw):
    raw = raw.split(':')
    values = ['0x' + s for s in raw]
    values = [int(v,16) for v in values]
    return values

def process_rgb(rgb, version):
    rgb = rgb.split(',')
    if len(rgb) < 3: print_error('Must have three color values (0-255) for R,G,B')

    values = [int(v) for v in rgb]
    values.insert(0,49) # add header

    # this version has an extra zero in the body
    if version == "AK001-ZJ2101":
        values.extend([0])

    values.extend([0,240,15]) # add tail
    return values

def print_error(message):
    print('\n' + esc('31;1') + ' ERROR' + esc(0) + ' : ' + message)
    print(' Run with -h for help.\n')
    sys.exit()

def esc(code):
    return f'\033[{code}m'

def Main(args):
    parser = ArgumentParser()
    parser.add_argument("-ip", help="provide the IP for the lightbulb; i.e. -ip 192.168.2.2")
    parser.add_argument("-raw", help="accept colon separated raw hex string; i.e. -raw 71:23:0f")
    parser.add_argument("-rgb", help="accept comma separated rgb values; i.e. -rgb 100,155,75")
    args = parser.parse_args()

    if args.ip is None:
        print_error('Must provide IP.')

    if args.raw is not None:
        values = process_raw(args.raw)

    if args.rgb is not None:
        version = get_version(args.ip)
        if version is None: sys.exit()
        values = process_rgb(args.rgb, version)

    if 'values' in locals():
        send(args.ip, values)
    else:
        print_error('Must provide raw hex or rgb values.')

if __name__ == '__main__':
    Main(sys.argv)
