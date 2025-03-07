"""Sepia effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect

class SepiaEffect(BaseEffect):
    """Applies a vintage brownish tone to the image"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'intensity': {
                'default': 0.7,  # Changed default to be less intense
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'label': 'Intensity'
            }
        }
    
    def apply(self, image, intensity=0.7, **kwargs):
        """Apply sepia effect to the image with adjustable intensity"""
        image = self.ensure_valid_image(image)
        
        # Fixed sepia conversion matrix with proper values
        base_sepia = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        
        # Create identity matrix (no effect)
        identity = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        
        # Linear interpolation between identity and sepia matrices
        sepia_matrix = identity * (1 - intensity) + base_sepia * intensity
        
        # Convert to uint8 to ensure compatibility
        img_array = np.array(image, dtype=np.float32)
        
        # Apply the transformation in a safer way
        result = np.zeros_like(img_array)
        for i in range(3):
            for j in range(3):
                result[:,:,i] += img_array[:,:,j] * sepia_matrix[i,j]
                
        # Clip and convert back to uint8
        return np.clip(result, 0, 255).astype(np.uint8)
