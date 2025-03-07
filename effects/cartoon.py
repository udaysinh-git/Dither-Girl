"""Cartoon effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect

class CartoonEffect(BaseEffect):
    """Transforms the image to look like a cartoon or drawing"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'strength': {
                'default': 7,
                'min': 3,
                'max': 15,
                'step': 1,
                'label': 'Strength'
            },
            'style': {
                'default': 0,
                'min': 0,
                'max': 2,
                'step': 1,
                'label': 'Style'
            }
        }
    
    def apply(self, image, strength=7, style=0, **kwargs):
        """Apply cartoon effect with adjustable parameters"""
        image = self.ensure_valid_image(image)
        
        try:
            # Convert parameters to integers
            strength = int(strength)
            style = int(style)
            
            # Ensure strength is odd
            if strength % 2 == 0:
                strength += 1
                
            # Style 0: Standard cartoon
            if style == 0:
                # Remove noise while preserving edges
                color = cv2.bilateralFilter(image, d=9, sigmaColor=strength*10, sigmaSpace=strength)
                
                # Edge detection
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                gray = cv2.medianBlur(gray, 5)
                edges = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                    cv2.THRESH_BINARY, strength, 3
                )
                
                # Combine edges with color
                edges_3ch = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                cartoon = cv2.bitwise_and(color, edges_3ch)
                
            # Style 1: Simplified cartoon with fewer details
            elif style == 1:
                # Strong smoothing with pyramids
                color = cv2.pyrMeanShiftFiltering(image, 15, strength*10, 2)
                
                # Simplified edges
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                gray = cv2.medianBlur(gray, strength)
                edges = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, strength*2+1, strength
                )
                
                # Combine
                edges_3ch = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                cartoon = cv2.bitwise_and(color, edges_3ch)
                
                # Enhance colors for comic-like look
                hsv = cv2.cvtColor(cartoon, cv2.COLOR_RGB2HSV)
                h, s, v = cv2.split(hsv)
                s = np.clip(s * 1.4, 0, 255).astype(np.uint8)  # Boost saturation
                hsv = cv2.merge([h, s, v])
                cartoon = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                
            # Style 2: Sketchy cartoon
            else:
                # Edge-preserving filter
                color = cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)
                
                # Get strong edges
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                blurred = cv2.GaussianBlur(gray, (0, 0), 3)
                edges = cv2.divide(gray, blurred, scale=256)
                
                # Combine
                cartoon = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                
                # Blend with color for a sketchy look
                cartoon = cv2.addWeighted(color, 0.7, cartoon, 0.3, 0)
            
            return cartoon
        
        except Exception as e:
            print(f"Error in cartoon effect: {str(e)}")
            # Fallback to a simpler cartoon effect
            return self._simple_cartoon(image)
            
    def _simple_cartoon(self, image):
        # Simple fallback cartoon effect
        color = cv2.bilateralFilter(image, 9, 250, 250)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        return cv2.bitwise_and(color, edges)
