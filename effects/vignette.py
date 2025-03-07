"""Vignette effect implementation"""
import numpy as np
from effects.base import BaseEffect

class VignetteEffect(BaseEffect):
    """Darkens the corners and edges of the image"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'intensity': {
                'default': 0.5,
                'min': 0.1,
                'max': 1.0,
                'step': 0.01,
                'label': 'Intensity'
            }
        }
    
    def apply(self, image, intensity=0.5, **kwargs):
        """Apply vignette effect with adjustable intensity"""
        image = self.ensure_valid_image(image)
        height, width = image.shape[:2]
        
        # Generate a radial gradient mask
        X = np.linspace(-1, 1, width)[np.newaxis, :]
        Y = np.linspace(-1, 1, height)[:, np.newaxis]
        radius = np.sqrt(X**2 + Y**2)
        
        # Normalize radius to [0, 1] and apply intensity
        mask = 1 - np.clip(radius * intensity * 1.5, 0, 1)
        mask = np.dstack([mask, mask, mask])
        
        # Apply the vignette mask to the image
        vignetted = image * mask
        return vignetted.astype(np.uint8)
