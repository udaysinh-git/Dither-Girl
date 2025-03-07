"""Base effect class that all effects should inherit from"""
import abc
import numpy as np

class BaseEffect(abc.ABC):
    """Abstract base class for image effects"""
    
    @property
    def name(self):
        """The name of the effect"""
        return self.__class__.__name__.replace('Effect', '')
    
    @property
    def description(self):
        """Description of what the effect does"""
        return self.__doc__
    
    @property
    def has_params(self):
        """Whether the effect has adjustable parameters"""
        return False
    
    @property
    def params(self):
        """Dictionary of parameters with default values and ranges"""
        return {}
    
    @abc.abstractmethod
    def apply(self, image, **kwargs):
        """Apply the effect to the image with the given parameters"""
        pass
    
    def ensure_valid_image(self, image):
        """Validate and ensure image is in proper format"""
        if image is None:
            raise ValueError("Image cannot be None")
        if not isinstance(image, np.ndarray):
            raise TypeError("Image must be a numpy array")
        return image
