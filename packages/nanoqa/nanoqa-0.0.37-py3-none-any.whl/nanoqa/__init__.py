import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - [%(asctime)s] - [%(name)s, line %(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)
logging.getLogger("fontTools.subset").setLevel(logging.CRITICAL)
