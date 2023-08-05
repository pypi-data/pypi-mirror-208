#!/usr/bin/env bash
import argparse
import os
import sys


def build(args):
    path = os.path.join(os.path.dirname(__file__), "src")
    gcc = "gcc -fPIC -shared -o"

    cmd_list = []
    if args.buf:
        cmd_list.append("{} {} buf.c buf.h".format(gcc, os.path.join(os.path.pardir, "buf.so")))

    for cmd in cmd_list:
        cmd = "cd {}; {}".format(path, cmd)
        print("# {}".format(cmd))

        if os.system(cmd) >> 8:
            raise RuntimeError('{} failed!'.format(cmd))

    print("Succeed.")


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Build')

    PARSER.add_argument('-b', '--buf', action='store_true', help='Build buffer')

    ARGS = PARSER.parse_args()

    sys.exit(build(ARGS))
