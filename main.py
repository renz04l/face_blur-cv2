import argparse
import os
#import shutil
import subprocess
import cv2 as cv
import numpy as np
from tqdm import tqdm

from utils import check_ffmpeg
# use FaceDetectorYN !!!

SUPPORTED_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv")

'''
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        raise SystemError("Add FFmpeg to PATH!")
'''

def apply_blur(roi, strength):
    k = strength if strength % 2 != 0 else strength + 1
    return cv.GaussianBlur(roi, (k, k), 30)


def apply_pixelation(roi, blocks):
    (h, w) = roi.shape[:2]
    x_steps = max(1, w // blocks)
    y_steps = max(1, h // blocks)
    
    small = cv.resize(roi, (x_steps, y_steps), interpolation=cv.INTER_LINEAR)
    return cv.resize(small, (w, h), interpolation=cv.INTER_NEAREST)


def process_video(file_path, output_dir, mode, blur_strength, pixel_blocks):
    filename = os.path.basename(file_path)
    base_name, _ = os.path.splitext(filename)
    
    temp_video_path = f"temp_{base_name}.mp4"
    final_output_path = os.path.join(output_dir, f"{base_name}_{mode}.mp4")

    cap = cv.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"Error opening file: {filename}")
        return

    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    fourcc = cv.VideoWriter_fourcc(*"mp4v")
    out = cv.VideoWriter(temp_video_path, fourcc, fps, (width, height))

    face_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")

    print(f"\n State: {filename} ({total_frames} frames) - Mode: {mode}")
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

            if mode == "pixelate":
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

    print(f"OK: {final_output_path}")

# change
def parse_args():
    parser = argparse.ArgumentParser(description="Batch face blur and pixelation for videos")
    
    parser.add_argument(
        "-m", "--mode",
        choices=["blur", "pixelate"],
        default="blur",
        help="Mode to censor faces :  'pixelate' or 'blur' [default]"
    )
    parser.add_argument(
        "-b", "--blur-strength",
        type=int,
        default=51,
        help="Blur Intensity (odd integer) lower = more visible [default: 51]"
    )
    parser.add_argument(
        "-p", "--pixel-blocks",
        type=int,
        default=12,
        help="Pixel dimensions (integer) lower = bigger pixel [default: 12]"
    )
    parser.add_argument(
        "-i", "--input",
        default="input_videos",
        help="Input folder [default: input_videos]"
    )
    parser.add_argument(
        "-o", "--output",
        default="output_videos",
        help="Output folder  [default: output_videos]"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    check_ffmpeg()

    os.makedirs(args.input, exist_ok=True)
    os.makedirs(args.output, exist_ok=True)

    files = [f for f in os.listdir(args.input) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    if not files:
        print(f"Not found any supported file in ./{args.input}/.")
        return

    print(f"Found {len(files)} videos in '{args.input}'.")
    for file in files:
        full_path = os.path.join(args.input, file)
        process_video(
            file_path=full_path,
            output_dir=args.output,
            mode=args.mode,
            blur_strength=args.blur_strength,
            pixel_blocks=args.pixel_blocks
        )


if __name__ == "__main__":
    main()