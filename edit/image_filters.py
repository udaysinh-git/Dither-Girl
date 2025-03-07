import cv2
import numpy as np

class ImageFilters:
    def adjust_brightness(self, image, value):
        """Adjust the brightness of an image"""
        return np.clip(image + (value * 2.55), 0, 255).astype(np.uint8)
    
    def adjust_contrast(self, image, value):
        """Adjust the contrast of an image"""
        factor = (259 * (value + 255)) / (255 * (259 - value))
        def contrast(c):
            return np.clip(128 + factor * (c - 128), 0, 255).astype(np.uint8)
        return contrast(image)
    
    def adjust_saturation(self, image, value):
        """Adjust the saturation of an image"""
        hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv_image)
        
        # Adjust saturation channel
        s = np.clip(s * (1 + value/100), 0, 255).astype(np.uint8)
        
        # Merge channels back
        hsv_image = cv2.merge([h, s, v])
        return cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)
    
    def adjust_sharpness(self, image, value):
        """Apply sharpness filter to an image"""
        kernel = np.array([[-1, -1, -1],
                          [-1, 9 + value/10, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)
    
    def apply_blur(self, image, value):
        """Apply Gaussian blur to an image"""
        if value % 2 == 0:  # Ensure kernel size is odd
            value += 1
        return cv2.GaussianBlur(image, (value, value), 0)
    
    def apply_grayscale(self, image):
        """Convert image to grayscale"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    def apply_negative(self, image):
        """Apply negative effect to an image"""
        return 255 - image
