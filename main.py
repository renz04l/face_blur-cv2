import argparse
import os
import logging
from utils import check_ffmpeg
from processor import process_video, SUPPORTED_EXTENSIONS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)-8s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# parser
def parse_args():
    parser = argparse.ArgumentParser(description="Batch face blur and pixelation for videos")
    
    parser.add_argument(
        "-m", "--mode",
        choices=["blur", "privacy", "pixelate"],
        default="blur",
        help="Mode to censor faces :  'privacy', 'pixelate' or 'blur' [default]"
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

    args = parser.parse_args()
    
    if args.pixel_blocks < 1:
        parser.error("--pixel-blocks must be greater than 0")
    if args.blur_strength < 1:
        parser.error("--blur-strength must be positive")
    if args.blur_strength % 2 == 0:
        parser.error("--blur-strength must be an odd integer")

    return parser.parse_args()


def main():
    args = parse_args()
    check_ffmpeg()

    os.makedirs(args.output, exist_ok=True)

    if not os.path.exists(args.input):
        os.makedirs(args.input, exist_ok=True)
        logger.info(f"Created missing input folder: '{args.input}'")
        logger.warning(f"Created input folder '{args.input}'. Please put your videos inside and run again.")
        return

    files = [
        f for f in os.listdir(args.input) 
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]
    
    if not files:
        logger.warning(f"Not found any supported file in ./{args.input}/.")
        logger.info(f"Add some videos ({SUPPORTED_EXTENSIONS}) to the folder and run again.")
        return

    logger.info(f"Found {len(files)} videos in '{args.input}'.")
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