#!/usr/bin/env python3

import os
import shutil

for root, dirs, files in os.walk('.'):
    base_dir = os.path.abspath('.')
    # ignore curent directory
    if root == '.':
        continue
    print("Direcotry: " + root)
    for i in files:
        file_name = os.path.join(base_dir, i)
        # rename the file of the same name
        while os.path.exists(file_name):
            a, b = os.path.splitext(file_name)
            file_name = a + '_' + b
        shutil.copyfile(os.path.join(root, i), file_name)
    print()
