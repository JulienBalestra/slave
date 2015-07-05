import logging
from os.path import dirname, abspath

formatter = logging.Formatter('%(asctime)-8s %(levelname)-8s %(module)-8s %(message)s')

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(formatter)

fileHandler = logging.FileHandler(dirname(dirname(abspath(__file__))) + '/logs.txt')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)


def get_logger(name):
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(consoleHandler)
	logger.addHandler(fileHandler)
	return logger