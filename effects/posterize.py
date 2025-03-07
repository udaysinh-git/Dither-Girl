"""Posterize effect implementation"""
import numpy as np
from effects.base import BaseEffect

class PosterizeEffect(BaseEffect):
    """Reduces the number of colors to create a poster-like effect"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'levels': {
                'default': 4,
                'min': 2,
                'max': 8,
                'step': 1,
                'label': 'Color Levels'
            }
        }
    
    def apply(self, image, levels=4, **kwargs):
        """Apply posterize effect with adjustable color levels"""
        image = self.ensure_valid_image(image)
        
        # Convert levels to integer and clamp
        levels = int(levels)
        levels = max(2, min(8, levels))
        
        # Calculate the division factor
        factor = 255 / (levels - 1)
        
        # Apply to each channel for better control
        result = np.zeros_like(image)
        for i in range(3):
            channel = image[:, :, i]
            # Quantize the pixel values
            result[:, :, i] = np.floor(channel / factor + 0.5) * factor
            
        return result.astype(np.uint8)
