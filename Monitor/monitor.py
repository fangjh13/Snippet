#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''利用`watchdog`自动追踪`sys.argv[1]`的文件夹，并打印log'''

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = LoggingEventHandler()
    observe = Observer()
    observe.schedule(event_handler, path, True)
    observe.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observe.stop()
    observe.join()
