import logging

logging.basicConfig(
    filename="moodleNotify.log",
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s:%(message)s",
)
logger = logging.getLogger("moodleNotify")
