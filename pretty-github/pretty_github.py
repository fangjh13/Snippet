#/usr/bin/evn python3
# -*- coding: utf-8 -*-

import datetime
import random
import subprocess


def run(start, end):
	start = datetime.datetime(
		int(start[:4]), int(start[4:6]), int(start[6:]))
	end = datetime.datetime(
		int(end[:4]), int(end[4:6]), int(end[6:]))
	interval = datetime.timedelta(
		hours=random.randint(1, 13), seconds=random.randint(0, 31))

	days = end - start + datetime.timedelta(days=1)
	for i in range(days.days):
		interval = datetime.timedelta(
			hours=random.randint(1, 13),
			seconds=random.randint(0, 31))
		timestamp = start + interval
		with open('forge.txt', 'a+') as f:
			f.write(timestamp.isoformat() + '\n')
		subprocess.call('git add .', shell=True)
		subprocess.call(
			"git commit --date='{0}' -m 'commit {0}'".format(
				timestamp.isoformat()), shell=True)
		start += datetime.timedelta(days=1)


if __name__ == '__main__':
	# format `YYYYMMDD`
	run('20160410', '20170205 ')
