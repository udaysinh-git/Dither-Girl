"""Edge detection effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect

class EdgeDetectionEffect(BaseEffect):
    """Detects and highlights edges in the image"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'threshold': {
                'default': 40,  # Lower default for more visible edges
                'min': 10,
                'max': 150,
                'step': 1,
                'label': 'Sensitivity'
            },
            'color': {
                'default': 0,
                'min': 0,
                'max': 3,
                'step': 1,
                'label': 'Color Mode'
            }
        }
    
    def apply(self, image, threshold=40, color=0, **kwargs):
        """Apply edge detection with adjustable parameters"""
        image = self.ensure_valid_image(image)
        
        try:
            # Convert to grayscale and apply Gaussian blur
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply Canny edge detection
            edges = cv2.Canny(blurred, threshold, threshold * 2)
            
            # Different color modes
            color_mode = int(color)
            
            if color_mode == 0:  # White edges on black background
                result = np.zeros_like(image)
                result[edges > 0] = [255, 255, 255]
            
            elif color_mode == 1:  # Black edges on white background
                result = np.ones_like(image) * 255
                result[edges > 0] = [0, 0, 0]
            
            elif color_mode == 2:  # Original color edges on black
                result = np.zeros_like(image)
                mask = edges > 0
                result[mask] = image[mask]
            
            else:  # Colored edges (blue)
                result = np.zeros_like(image)
                result[edges > 0] = [255, 255, 0]  # Yellow edges
            
            return result
            
        except Exception as e:
            print(f"Error in edge detection: {str(e)}")
            # Fallback method
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
