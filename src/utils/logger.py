import sys
import os
from loguru import logger


logger.remove()
logger.add(sys.stderr, level="INFO")

os.makedirs("../../logs", exist_ok=True)
logger.add("../../logs/training.log", level="DEBUG")

if __name__ == "__main__":
    logger.info("Testing whether logging works correctly")
