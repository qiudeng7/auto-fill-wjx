from loguru import logger
import os

parentPath = os.path.dirname(os.path.abspath(__file__))
logDirPath = os.path.join(parentPath, "logs")
logPath = os.path.join(logDirPath, "log.log")

if not os.path.exists(logDirPath):
    os.mkdir(logDirPath)

logger.add(logPath, rotation="10 MB")
logger.info("loguru logger started")
