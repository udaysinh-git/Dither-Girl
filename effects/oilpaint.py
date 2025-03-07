"""Oil painting effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect

class OilPaintEffect(BaseEffect):
    """Creates an oil painting effect"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'radius': {
                'default': 4,
                'min': 1,
                'max': 10,
                'step': 1,
                'label': 'Brush Size'
            },
            'intensity': {
                'default': 5,
                'min': 1,
                'max': 20,
                'step': 1,
                'label': 'Intensity'
            }
        }
    
    def apply(self, image, radius=4, intensity=5, **kwargs):
        """Apply oil painting effect with adjustable parameters"""
        image = self.ensure_valid_image(image)
        
        # Convert to integer
        radius = int(radius)
        intensity = int(intensity)
        
        try:
            # Use OpenCV's xphoto module for oil painting
            # If not available, fall back to a custom implementation
            try:
                # Try using xphoto oil painting filter if available
                oil = cv2.xphoto.oilPainting(image, radius, intensity)
                return oil
            except:
                # Fall back to custom implementation
                return self._custom_oil_paint(image, radius, intensity)
                
        except Exception as e:
            print(f"Error in oil paint effect: {str(e)}")
            # Fall back to bilateral filter for a similar effect
            return cv2.bilateralFilter(image, 9, 75, 75)
    
    def _custom_oil_paint(self, image, radius, intensity):
        """Custom oil paint implementation when cv2.xphoto is not available"""
        # Convert to float32 for processing
        img_float = image.astype(np.float32) / 255.0
        
        # Apply bilateral filter for smoothing while preserving edges
        smoothed = cv2.bilateralFilter(image, radius*2+1, intensity*10, intensity*5)
        
        # Add some texture using a median filter
        texture = cv2.medianBlur(smoothed, radius*2+1)
        
        # Enhance edges for a painted look
        edge_enhancer = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
        edges = cv2.filter2D(texture, -1, edge_enhancer)
        
        # Increase color saturation slightly
        hsv = cv2.cvtColor(edges, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        s = np.clip(s * 1.3, 0, 255).astype(np.uint8)  # Increase saturation
        hsv = cv2.merge([h, s, v])
        
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
