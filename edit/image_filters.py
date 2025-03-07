import cv2
import numpy as np
import math

class ImageFilters:
    def adjust_brightness(self, image, value):
        """Adjust the brightness of an image"""
        return np.clip(image + (value * 2.55), 0, 255).astype(np.uint8)
    
    def adjust_contrast(self, image, value):
        """Adjust the contrast of an image"""
        # Convert the -100 to 100 range to a more suitable contrast factor
        # Use a more gradual approach for better control
        if value > 0:
            # For positive values, use a gentler scaling to avoid extreme contrast
            factor = 1.0 + (value / 100.0) * 0.8
        else:
            # For negative values, reduce contrast gradually
            factor = 1.0 + (value / 100.0)
        
        # Apply contrast adjustment while preserving average brightness
        mean = np.mean(image, axis=(0, 1))
        adjusted = mean + factor * (image - mean)
        
        return np.clip(adjusted, 0, 255).astype(np.uint8)
    
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
    
    # New filters
    
    def apply_sepia(self, image, intensity=1.0):
        """Apply sepia tone effect to an image with adjustable intensity"""
        # Base sepia conversion matrix
        base_sepia = np.array([[0.393, 0.769, 0.189],
                               [0.349, 0.686, 0.168],
                               [0.272, 0.534, 0.131]])
        
        # Adjust the sepia effect based on intensity
        if intensity != 1.0:
            # Blend between identity matrix and sepia matrix
            identity = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
            sepia_matrix = identity * (1 - intensity) + base_sepia * intensity
        else:
            sepia_matrix = base_sepia
        
        # Apply the sepia matrix transformation
        sepia_img = np.array(image, dtype=np.float64)
        sepia_img = cv2.transform(sepia_img, sepia_matrix)
        
        # Clip and convert back to uint8
        return np.clip(sepia_img, 0, 255).astype(np.uint8)
    
    def apply_vignette(self, image, intensity=0.5):
        """Apply vignette effect to an image with adjustable intensity"""
        height, width = image.shape[:2]
        
        # Generate a radial gradient mask
        X = np.linspace(-1, 1, width)[np.newaxis, :]
        Y = np.linspace(-1, 1, height)[:, np.newaxis]
        radius = np.sqrt(X**2 + Y**2)
        
        # Normalize radius to [0, 1] and apply intensity
        mask = 1 - np.clip(radius * intensity * 1.5, 0, 1)
        mask = np.dstack([mask, mask, mask])
        
        # Apply the vignette mask to the image
        vignetted = image * mask
        return vignetted.astype(np.uint8)
    
    def apply_warm(self, image, value=30):
        """Apply warm temperature effect by increasing red and decreasing blue"""
        # Copy the image to avoid modifying the original
        warm_img = image.copy().astype(np.int16)
        
        # Increase red, decrease blue
        warm_img[:, :, 0] = np.clip(warm_img[:, :, 0] + value, 0, 255)  # R
        warm_img[:, :, 2] = np.clip(warm_img[:, :, 2] - value, 0, 255)  # B
        
        return warm_img.astype(np.uint8)
    
    def apply_cool(self, image, value=30):
        """Apply cool temperature effect by increasing blue and decreasing red"""
        # Copy the image to avoid modifying the original
        cool_img = image.copy().astype(np.int16)
        
        # Increase blue, decrease red
        cool_img[:, :, 2] = np.clip(cool_img[:, :, 2] + value, 0, 255)  # B
        cool_img[:, :, 0] = np.clip(cool_img[:, :, 0] - value, 0, 255)  # R
        
        return cool_img.astype(np.uint8)
    
    def apply_edge_detection(self, image, threshold1=100, threshold2=200):
        """Apply Canny edge detection to an image with adjustable thresholds"""
        # Convert to grayscale first
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Canny edge detection with custom thresholds
        edges = cv2.Canny(gray, threshold1, threshold2)
        
        # Convert back to RGB
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    
    def apply_posterize(self, image, levels=4):
        """Reduce the number of colors to create a poster-like effect"""
        # Ensure levels is at least 2
        levels = max(2, levels)
        
        # Calculate the division factor
        factor = 255 / (levels - 1)
        
        # Round to the nearest level
        poster_img = np.round(image / factor) * factor
        
        return poster_img.astype(np.uint8)
    
    def apply_emboss(self, image):
        """Apply emboss effect to an image"""
        # Define the emboss kernel
        kernel = np.array([[-2, -1, 0],
                           [-1, 1, 1],
                           [0, 1, 2]])
        
        # Apply the kernel
        emboss_img = cv2.filter2D(image, -1, kernel) + 128
        
        # Clip values and convert to uint8
        return np.clip(emboss_img, 0, 255).astype(np.uint8)
    
    def apply_cartoon(self, image):
        """Apply cartoon effect to an image"""
        # Apply bilateral filter to reduce noise and keep edges sharp
        color = cv2.bilateralFilter(image, 9, 300, 300)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply median blur
        gray = cv2.medianBlur(gray, 5)
        
        # Detect and enhance edges
        edges = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY, 9, 9
        )
        
        # Convert edges back to RGB
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        # Combine color and edges
        cartoon = cv2.bitwise_and(color, edges)
        
        return cartoon
