import os
import shutil
import numpy as np
import pytest
from unittest import mock
'''
python -m pytest -v           
'''
# import function from effects and utils
from effects import apply_blur, apply_pixelation
from utils import check_ffmpeg

def test_apply_blur():
    # fake white roi (Region of Interest) 100x100 pixel
    roi = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    # blur 15 intensity
    strength = 15
    blurred_roi = apply_blur(roi, strength)
    
    # 1 same shape
    assert blurred_roi.shape == roi.shape
    # 2 uint8
    assert blurred_roi.dtype == np.uint8

def test_apply_blur_even_strength():
    # even to odd, GaussianBlur
    roi = np.ones((50, 50, 3), dtype=np.uint8) * 128
    
    # try with 10 for cv.GaussianBlur
    try:
        blurred_roi = apply_blur(roi, 10)
        assert blurred_roi.shape == (50, 50, 3)
    except Exception as e:
        pytest.fail(f"apply_blur failed with even strength: {e}")

def test_apply_pixelation():
    # other fake ROI checkerboard pattern
    roi = np.zeros((100, 100, 3), dtype=np.uint8)
    roi[0:50, 0:50] = 255
    roi[50:100, 50:100] = 255
    
    blocks = 10
    pixelated_roi = apply_pixelation(roi, blocks)
    
    # 1 same shape
    assert pixelated_roi.shape == roi.shape
    # 2 uint8
    assert pixelated_roi.dtype == np.uint8

@mock.patch('shutil.which')
def test_check_ffmpeg_installed(mock_which):
    mock_which.return_value = "/usr/bin/ffmpeg"
    
    # check ffmpeg existing
    try:
        check_ffmpeg()
    except SystemError:
        pytest.fail("check_ffmpeg() SystemError!")

@mock.patch('shutil.which')
def test_check_ffmpeg_missing(mock_which):
    mock_which.return_value = None
    
    # check ffmpeg not existing (SystemError)
    with pytest.raises(SystemError, match="Add FFmpeg to PATH!"):
        check_ffmpeg()

