#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib


def verify_checksum(path):
	hash_sha256 = hashlib.sha256()
	with open(path, 'rb') as f:
		for chunk in iter(lambda: f.read(2048), b''):
			hash_sha256.update(chunk)
	return hash_sha256.hexdigest()


if __name__ == '__main__':
	import sys
	file_path = sys.argv[1]
	print('verify the {} sha-256 checksum...'.format(file_path))
	print('DIGEST: ' + verify_checksum(file_path))
