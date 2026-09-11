import shutil
import logging

logger = logging.getLogger(__name__)

def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        logger.critical("FFmpeg not found! Please install and add to PATH.")
        raise SystemError("Add FFmpeg to PATH!")