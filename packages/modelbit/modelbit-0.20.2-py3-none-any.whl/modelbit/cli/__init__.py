#!/usr/bin/env python3

import logging
import os


def main() -> None:
  from . import cmdline
  cmdline.processArgs()


if __name__ == '__main__':
  main()
