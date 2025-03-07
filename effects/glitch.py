"""Glitch effect implementation"""
import cv2
import numpy as np
from effects.base import BaseEffect
import random

class GlitchEffect(BaseEffect):
    """Creates a digital glitch/corruption effect"""
    
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
            },
            'seed': {
                'default': 42,
                'min': 0,
                'max': 100,
                'step': 1,
                'label': 'Variation'
            }
        }
    
    def apply(self, image, intensity=0.5, seed=42, **kwargs):
        """Apply digital glitch effect with adjustable intensity"""
        image = self.ensure_valid_image(image)
        
        # Set random seed for reproducible results with same parameters
        random.seed(int(seed))
        np.random.seed(int(seed))
        
        # Get image dimensions
        h, w, c = image.shape
        result = image.copy()
        
        try:
            # Number of glitch operations based on intensity
            num_glitches = int(10 * intensity)
            
            # 1. Channel shift
            for i in range(int(num_glitches / 2)):
                # Select a random channel
                ch = random.randint(0, 2)
                
                # Define shift amount based on intensity
                shift_x = random.randint(int(-w*0.05*intensity), int(w*0.05*intensity))
                shift_y = random.randint(int(-h*0.05*intensity), int(h*0.05*intensity))
                
                # Apply the shift to the selected channel
                if shift_x > 0:
                    result[:, shift_x:, ch] = result[:, :-shift_x, ch]
                elif shift_x < 0:
                    result[:, :shift_x, ch] = result[:, -shift_x:, ch]
                
                if shift_y > 0:
                    result[shift_y:, :, ch] = result[:-shift_y, :, ch]
                elif shift_y < 0:
                    result[:shift_y, :, ch] = result[-shift_y:, :, ch]
            
            # 2. Random block shifts
            for i in range(num_glitches):
                # Select random position and size
                x1 = random.randint(0, w - 50)
                y1 = random.randint(0, h - 20)
                h_block = random.randint(1, int(h * 0.1 * intensity))
                w_block = random.randint(int(w * 0.05), int(w * 0.3))
                
                # Set shift amount
                shift = random.randint(int(5 * intensity), int(40 * intensity))
                
                # Ensure we stay within bounds
                if x1 + w_block < w and y1 + h_block < h and x1 + w_block + shift < w:
                    # Copy and shift the block
                    block = image[y1:y1+h_block, x1:x1+w_block].copy()
                    result[y1:y1+h_block, x1+shift:x1+w_block+shift] = block
            
            # 3. Add some color noise - fixed to handle masks correctly
            if random.random() < intensity * 0.8:
                noise = np.zeros_like(image)
                # Create a single-channel mask (h,w) instead of (h,w,c)
                noise_mask = (np.random.random((h, w)) < intensity * 0.1).astype(np.uint8)
                # Generate random noise
                for ch in range(3):
                    noise[:, :, ch] = np.random.randint(0, 255, (h, w))
                
                # Apply noise only where the mask is 1
                noise_part = cv2.bitwise_and(noise, noise, mask=noise_mask)
                # Keep original pixels where the mask is 0
                inverted_mask = cv2.bitwise_not(noise_mask)
                original_part = cv2.bitwise_and(result, result, mask=inverted_mask)
                # Combine both parts
                result = cv2.add(original_part, noise_part)
            
            return result
        
        except Exception as e:
            print(f"Error in glitch effect: {str(e)}")
            return image  # Return original if the effect fails
