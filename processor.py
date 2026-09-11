import os
import subprocess
import logging
import tempfile
import shutil
import cv2 as cv
from tqdm import tqdm
from effects import apply_blur, apply_pixelation

SUPPORTED_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv")

logger = logging.getLogger(__name__)

def process_video(file_path, output_dir, mode, blur_strength, pixel_blocks):
    filename = os.path.basename(file_path)
    base_name, _ = os.path.splitext(filename)
    
    temp_video_path = f"temp_{base_name}.mp4"
    final_output_path = os.path.join(output_dir, f"{base_name}_{mode}.mp4")

    cap = cv.VideoCapture(file_path)
    if not cap.isOpened():
        logger.error(f"Error opening file: {filename}")
        return

    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    fourcc = cv.VideoWriter_fourcc(*"mp4v")
    out = cv.VideoWriter(temp_video_path, fourcc, fps, (width, height))

    face_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")

    logger.info(f"File: {filename} ({total_frames} frames) - Mode: {mode}")
    pbar = tqdm(total=total_frames, unit="frame")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(30, 30)
        )

        for (x, y, w, h) in faces:
            pad_x = int(w * 0.1)
            pad_y = int(h * 0.1)
            
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(width, x + w + pad_x)
            y2 = min(height, y + h + pad_y)

            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            if mode == "privacy":
                frame[y1:y2, x1:x2] = (0, 0, 0)
            elif mode == "pixelate":
                frame[y1:y2, x1:x2] = apply_pixelation(roi, pixel_blocks)
            else:
                frame[y1:y2, x1:x2] = apply_blur(roi, blur_strength)

        out.write(frame)
        pbar.update(1)

    pbar.close()
    cap.release()
    out.release()

    #FFmpeg audio (add output)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", temp_video_path,
        "-i", file_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0?",
        "-shortest",
        final_output_path
    ]

    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)

    logger.info(f"OK: {final_output_path}")