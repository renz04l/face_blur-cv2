# Face Blur & Pixelation Batch Tool
Python script for automatic face detection and blurring (Gaussian blur or pixelation) in videos in batch mode, preserving the original audio track via FFmpeg (must be in system PATH)
## Installation
You need:
1. **[Python 3.8+](https://www.python.org/downloads/)**
2. **FFmpeg**:
    - **Ubuntu/Debian:** `apt install ffmpeg`
    - **Fedora:**  `dnf install ffmpeg`
    - **macOS:** `brew install ffmpeg`
    - **Windows:** download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add to PATH (or ```winget install Gyan.FFmpeg```).
Than clone the repository and install the dependency:
```bash
git clone https://github.com/renz04l/face_blur-cv2.git
cd face_blur-cv2
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Command-Line Arguments

| Flag | Long Flag         | Default         | Description                                             |
| ---- | ----------------- | --------------- | ------------------------------------------------------- |
| `-m` | `--mode`          | `blur`          | Obfuscation technique: `blur` or `pixelate`             |
| `-b` | `--blur-strength` | `51`            | Kernel size for Gaussian blur (**must an odd number**)  |
| `-p` | `--pixel-blocks`  | `12`            | Pixelation grid scale (**lower value = larger pixels**) |
| `-i` | `--input`         | `input_videos`  | Path to the directory containing source videos          |
| `-o` | `--output`        | `output_videos` | Path to the destination directory for processed videos  |
| `-h` | `--help`          |                 | Show help message and exit                              |

---
### Examples
#### 1. Default Run (Gaussian Blur)
Applies a standard Gaussian blur (strength: 51) to all videos in `input_videos/`:
```bash
python main.py
```
#### 2. Pixelation Mode
Censors faces using a mosaic pixel effect: 
```bash
python main.py -m pixelate
```
#### 3. Heavy Pixelation (Larger Blocks)
Reduces the block count to 6 for maximum anonymity:
```bash
python main.py -m pixelate -p 6
```
#### 4. Heavy Blur
Increases blur strength for strong obfusation:
```bash
python main.py -m blur -b 99
```
#### 5. Custom Directories
Specify custom input and output folder:
```bash
python main.py -i ./my_input -o ./censored
```

  
# To-do
- [ ] From **Haar Cascade** to **OpenCV YuNet** (FaceDetectorYN)
- [ ] Maybe **MediaPipe Face Detection (BlazeFace)** or **YOLO-Face o SCRFD**
- [ ] Add temporal tracking (ByteTrack, Norfair ...)
- [ ] EMA, Kalman and Feathering
- [ ] Reduce frame resolution for mapping fase
- [ ] Add result and diff gif on readme (blur/pixelate - haar version vs yunet version)
