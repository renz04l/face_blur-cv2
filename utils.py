import shutil

def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        raise SystemError("Add FFmpeg to PATH!")