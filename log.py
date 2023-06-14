# add logger to the project

import logging

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('log.log')  # file handler
fh.setLevel(logging.WARNING)  # set the log level for the file handler to DEBUG (all messages) and above 
fh.setFormatter(formatter)

ch = logging.StreamHandler()  # console handler
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# dont print the log to the console
logger.propagate = False

if __name__ == '__main__':
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')