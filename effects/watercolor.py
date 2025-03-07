"""Watercolor effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect

class WatercolorEffect(BaseEffect):
    """Creates a watercolor painting effect"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'strength': {
                'default': 50,
                'min': 10,
                'max': 500,
                'step': 1,
                'label': 'Strength'
            },
            'saturation': {
                'default': 1.2,
                'min': 0.8,
                'max': 2.0,
                'step': 0.05,
                'label': 'Saturation'
            }
        }
    
    def apply(self, image, strength=50, saturation=1.2, **kwargs):
        """Apply watercolor effect with adjustable parameters"""
        image = self.ensure_valid_image(image)
        
        try:
            # Cap the kernel size to OpenCV's limit (max 15)
            kernel_size = min(int(strength / 10) * 2 + 1, 15)
            # Make sure kernel size is odd
            if kernel_size % 2 == 0:
                kernel_size -= 1
            
            # Apply bilateral filter for edge preservation and smoothing
            bilateral = cv2.bilateralFilter(image, 9, 75, 75)
            
            # Apply median blur with the capped kernel size
            median = cv2.medianBlur(bilateral, kernel_size)
            
            # Enhance edges
            edges = cv2.Canny(median, 50, 150)
            edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
            edges_3channel = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            # Enhance colors/saturation
            hsv = cv2.cvtColor(median, cv2.COLOR_BGR2HSV).astype("float32")
            (h, s, v) = cv2.split(hsv)
            s = s * saturation
            s = np.clip(s, 0, 255)
            hsv = cv2.merge([h, s, v])
            saturated = cv2.cvtColor(hsv.astype("uint8"), cv2.COLOR_HSV2BGR)
            
            # Subtract edges from the saturated image
            result = cv2.subtract(saturated, edges_3channel)
            
            return result
            
        except Exception as e:
            print(f"Error applying watercolor effect: {str(e)}")
            return image  # Return original if the effect fails
