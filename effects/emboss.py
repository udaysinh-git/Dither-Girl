"""Emboss effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect

class EmbossEffect(BaseEffect):
    """Creates a 3D embossed effect"""
    
    def apply(self, image, **kwargs):
        """Apply emboss effect to the image"""
        image = self.ensure_valid_image(image)
        
        # Define the emboss kernel
        kernel = np.array([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
        ])
        
        # Apply the kernel
        emboss_img = cv2.filter2D(image, -1, kernel) + 128
        
        # Clip values and convert to uint8
        return np.clip(emboss_img, 0, 255).astype(np.uint8)
