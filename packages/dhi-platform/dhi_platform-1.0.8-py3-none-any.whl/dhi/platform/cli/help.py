#!/usr/bin/env python
import importlib
import os.path, sys
from dhi.platform.args import ClientArgs

def main():
    if len(sys.argv) > 1:
        module = importlib.import_module(sys.argv[1])
        dirname = module.__path__[0]
    else:
        dirname = os.path.dirname(__file__)
    ClientArgs.ListPackageModules(dirname)

if __name__ == '__main__':
    main()
