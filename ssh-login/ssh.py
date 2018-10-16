#!/usr/bin/env python3
import pexpect
import argparse
from configparser import ConfigParser


# can read from ini file
data = """
[admin]
192.168.70.200 = password
"""

def main(url):
    child = pexpect.spawn('ssh {0}'.format(url))
    child.expect("{}'s password: ".format(url))
    config = ConfigParser()
    user, host = url.split('@', 1)
    config.read_string(data)
    child.sendline(config[user][host])
    child.interact()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='My SSH client')
    parser.add_argument('address', help='remote user and server such as "foo@bar.com"')
    args = parser.parse_args()
    main(args.address)
