import pytesseract
import cv2
from PIL import Image
import numpy as np

def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)
    return text