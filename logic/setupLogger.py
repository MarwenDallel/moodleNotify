import logging
import os

if not os.path.exists('logs/'):
    os.mkdir('logs/')

logging.basicConfig(
    filename="logs/moodleNotify.log",
    level=logging.DEBUG,
    format="%(asctime)s %(name)s.%(module)s %(levelname)s:%(message)s",
)

logger = logging.getLogger("moodleNotify")
