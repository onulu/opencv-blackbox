#!/usr/bin/env python3

from logger import logger
from blackbox import BlackBox


def main():
    try:
        blackbox = BlackBox()
        blackbox.run()
    except Exception as e:
        logger.exception(f"Critical error in main: {str(e)}")


if __name__ == "__main__":
    main()
