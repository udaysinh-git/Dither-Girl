"""Grayscale effect implementation"""
import cv2
from effects.base import BaseEffect

class GrayscaleEffect(BaseEffect):
    """Converts an image to grayscale (black and white)"""
    
    def apply(self, image, **kwargs):
        """Apply grayscale effect to the image"""
        image = self.ensure_valid_image(image)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
