#!/usr/bin/env python3
"""
Units used
time: second (for now)
distance: meter
speed: meter / second
acceleration meter / second*seconds
power: W
energy: Wh
"""

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def main() -> None:
    log.info("Currently no default simulation setup.")


if __name__ == "__main__":
    main()
