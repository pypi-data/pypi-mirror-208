from zm.modules.betterDateTime import *
import logging as log
text_format = f'[ %(levelname)s ][ %(filename)s:%(lineno)d ][ %(asctime)s ]:  %(message)s'
date_format = f'{get_format(77)} | {create_format("%(short month)s %(day)s, %(year)s")}'
log_file = f'{get_datetime(create_format("%(short month)s-%(day)s-%(year)s_%(24h)s.%(m)s.%(s)s"))}.log'
file_path = './logs/'
fname = file_path + log_file
log.basicConfig(filename=fname, level=log.DEBUG, format=text_format, datefmt=date_format)
console = log.StreamHandler()
console.setLevel(log.DEBUG)
formatter = log.Formatter(text_format, date_format)
console.setFormatter(formatter)
log.getLogger('').addHandler(console)