import logging


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(module)s - %(levelname)s - %(message)s",
        filename="blackbox.log",
    )
    return logging.getLogger()


logger = setup_logger()
