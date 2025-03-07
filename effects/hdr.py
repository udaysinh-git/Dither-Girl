"""HDR effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect

class HDREffect(BaseEffect):
    """Creates an HDR-like tone-mapped effect with enhanced details"""
    
    @property
    def has_params(self):
        return True
    
    @property
    def params(self):
        return {
            'strength': {
                'default': 0.5,
                'min': 0.1,
                'max': 1.0,
                'step': 0.01,
                'label': 'Strength'
            },
            'saturation': {
                'default': 0.5,
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'label': 'Saturation'
            }
        }
    
    def apply(self, image, strength=0.5, saturation=0.5, **kwargs):
        """Apply HDR effect with adjustable strength"""
        image = self.ensure_valid_image(image)
        
        try:
            # Convert strength to proper range
            strength = min(1.0, max(0.1, strength))
            saturation = min(1.0, max(0.0, saturation))
            
            # Create multiple exposures
            under_exposed = np.clip(image * 0.7, 0, 255).astype(np.uint8)
            over_exposed = np.clip(image * 1.3, 0, 255).astype(np.uint8)
            
            # Apply detail enhancement with bilateral filtering
            detail = cv2.detailEnhance(image, sigma_s=strength*16, sigma_r=strength*0.2)
            
            # Create tone-mapped HDR effect - apply to the whole image at once
            hdr = cv2.createTonemapReinhard(gamma=1.0, intensity=1.0, 
                                           light_adapt=0.8, color_adapt=0.5)
            
            # Convert to float32 and apply tonemapping to the whole image
            # OpenCV expects BGR order for tonemapping
            if detail.shape[2] == 3:  # Make sure it's a 3-channel image
                detail_float = detail.astype(np.float32) / 255.0
                result_mapped = hdr.process(detail_float)
                result = np.clip(result_mapped * 255, 0, 255).astype(np.uint8)
            else:
                # Fallback if somehow the image doesn't have 3 channels
                result = detail
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)  # Use BGR for OpenCV
            l, a, b = cv2.split(lab)
            l_clahe = clahe.apply(l)
            lab = cv2.merge((l_clahe, a, b))
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)  # Convert back to BGR
            
            # Adjust saturation
            if saturation > 0:
                hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                s = np.clip(s * (1 + saturation), 0, 255).astype(np.uint8)
                hsv_enhanced = cv2.merge([h, s, v])
                result = cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2BGR)
            
            return result
            
        except Exception as e:
            print(f"Error in HDR effect: {str(e)}")
            # Fallback to simpler enhancement
            return cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)
