import cv2
import numpy as np

def load_image(file_path):
    """Load an image from file and convert to RGB"""
    image = cv2.imread(file_path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def save_image(file_path, image):
    """Save an image to a file with proper color conversion"""
    save_img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(file_path, save_img)
