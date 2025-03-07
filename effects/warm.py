"""Warm color effect implementation"""
import numpy as np
from effects.base import BaseEffect

class WarmEffect(BaseEffect):
    """Adds a warm temperature cast by enhancing reds and reducing blues"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'intensity': {
                'default': 30,
                'min': 10,
                'max': 50,
                'step': 1,
                'label': 'Intensity'
            }
        }
    
    def apply(self, image, intensity=30, **kwargs):
        """Apply warm temperature effect with adjustable intensity"""
        image = self.ensure_valid_image(image)
        
        # Copy the image to avoid modifying the original
        warm_img = image.copy().astype(np.int16)
        
        # Increase red, decrease blue
        warm_img[:, :, 0] = np.clip(warm_img[:, :, 0] + intensity, 0, 255)  # R
        warm_img[:, :, 2] = np.clip(warm_img[:, :, 2] - intensity, 0, 255)  # B
        
        return warm_img.astype(np.uint8)
