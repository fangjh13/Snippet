#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Generate HMAC-SHA1 Signature using Python 3'''


from functools import partial
from hashlib import sha1
from base64 import urlsafe_b64encode
import hmac

my_bytes = partial(bytes, encoding='utf-8')


def hmac_sha1(signing_str, secret_key):
	# convert bytes
	signing_byte, secret_byte = list(map(my_bytes, [signing_str, secret_key]))

	# digest of the bytes
	hashed = hmac.new(secret_byte, signing_byte, sha1).digest()

	# urlsafe base64 encode
	signature_byte = urlsafe_b64encode(hashed)

	return str(signature_byte, 'utf-8')
