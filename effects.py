import cv2 as cv

def apply_blur(roi, strength):
    k = strength if strength % 2 != 0 else strength + 1
    return cv.GaussianBlur(roi, (k, k), 30)

def apply_pixelation(roi, blocks):
    (h, w) = roi.shape[:2]
    x_steps = max(1, w // blocks)
    y_steps = max(1, h // blocks)
    
    small = cv.resize(roi, (x_steps, y_steps), interpolation=cv.INTER_LINEAR)
    return cv.resize(small, (w, h), interpolation=cv.INTER_NEAREST)