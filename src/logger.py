import logging


def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="blackbox.log",
    )
    return logging.getLogger()


logger = setup_logger()
