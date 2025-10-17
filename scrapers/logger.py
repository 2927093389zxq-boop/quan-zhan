import logging

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def log_info(msg: str):
    print(msg)
    logging.info(msg)

def log_error(msg: str):
    print(msg)
    logging.error(msg)