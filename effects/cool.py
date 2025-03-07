"""Cool color effect implementation"""
import numpy as np
from effects.base import BaseEffect

class CoolEffect(BaseEffect):
    """Adds a cool temperature cast by enhancing blues and reducing reds"""
    
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
        """Apply cool temperature effect with adjustable intensity"""
        image = self.ensure_valid_image(image)
        
        # Copy the image to avoid modifying the original
        cool_img = image.copy().astype(np.int16)
        
        # Increase blue, decrease red
        cool_img[:, :, 2] = np.clip(cool_img[:, :, 2] + intensity, 0, 255)  # B
        cool_img[:, :, 0] = np.clip(cool_img[:, :, 0] - intensity, 0, 255)  # R
        
        return cool_img.astype(np.uint8)
