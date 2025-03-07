"""Pixelate effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect

class PixelateEffect(BaseEffect):
    """Creates a pixel art effect by reducing resolution"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'block_size': {
                'default': 10,
                'min': 2,
                'max': 30,
                'step': 1,
                'label': 'Pixel Size'
            }
        }
    
    def apply(self, image, block_size=10, **kwargs):
        """Apply pixelation with adjustable block size"""
        image = self.ensure_valid_image(image)
        
        # Convert to integer
        block_size = int(max(2, block_size))
        
        # Get image dimensions
        h, w = image.shape[:2]
        
        # Calculate new dimensions
        h_new = h // block_size
        w_new = w // block_size
        
        # Resize down and then back up with nearest neighbor interpolation
        small = cv2.resize(image, (w_new, h_new), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
