#!/usr/bin/env python3

import os
import shutil


os.mkdir('newJoy')

for i in os.listdir('.'):
    if os.path.isfile(i):
        if i.endswith('.jpg') or i.endswith('.jpeg') or i.endswith('.png') or \
                i.endswith('.gif'):
            shutil.move(i, os.path.join('newJoy', i))
