"""Negative effect implementation"""
import numpy as np
from effects.base import BaseEffect

class NegativeEffect(BaseEffect):
    """Inverts all colors in the image"""
    
    def apply(self, image, **kwargs):
        """Apply negative effect to the image"""
        image = self.ensure_valid_image(image)
        return 255 - image
