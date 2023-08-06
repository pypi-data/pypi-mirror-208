# encoding: utf-8



# file: logger.py
# time: 11:43 

import os
import logging

logger = logging.Logger('kolibri', level='DEBUG')
stream_handler = logging.StreamHandler()

if os.environ.get('KASHGARI_DEV') == 'True':
    log_format = '%(asctime)s [%(levelname)s] %(name)s:%(filename)s:%(lineno)d - %(message)s'
else:
    log_format = '%(asctime)s [%(levelname)s] %(name)s - %(message)s'

stream_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(stream_handler)

if __name__ == "__main__":
    pass
