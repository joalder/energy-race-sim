import logging

# TODO: leave logging config up to the caller eventually
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("root").setLevel(logging.DEBUG)
