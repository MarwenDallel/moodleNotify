import logging
from resourcePath import resource_path

logging.basicConfig(filename=resource_path('moodleScrapper.log'), level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger('moodleScrapper')