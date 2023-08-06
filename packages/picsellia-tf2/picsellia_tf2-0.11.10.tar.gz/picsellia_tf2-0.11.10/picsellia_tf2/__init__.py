import os
import sys

from setuptools import find_packages

import picsellia_tf2

for p in find_packages(where=picsellia_tf2.__path__[0]):
    sys.path.append(os.path.join(picsellia_tf2.__path__[0], p.replace(".", "/")))

sys.path.append(picsellia_tf2.__path__[0])
sys.path.append(os.path.join(picsellia_tf2.__path__[0], "object_detection"))
sys.path.append(os.path.join(picsellia_tf2.__path__[0], "slim"))
