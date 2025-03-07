"""
Effects module for Dither Girl.
Contains all image effects that can be applied in the application.
"""

from effects.base import BaseEffect
from effects.grayscale import GrayscaleEffect
from effects.negative import NegativeEffect
from effects.sepia import SepiaEffect
from effects.vignette import VignetteEffect
from effects.warm import WarmEffect
from effects.cool import CoolEffect
from effects.edge import EdgeDetectionEffect
from effects.posterize import PosterizeEffect
from effects.emboss import EmbossEffect
from effects.cartoon import CartoonEffect
from effects.pixelate import PixelateEffect
from effects.watercolor import WatercolorEffect
from effects.glitch import GlitchEffect
from effects.hdr import HDREffect
from effects.oilpaint import OilPaintEffect

# Dictionary of all available effects for easy registration
EFFECTS = {
    'grayscale': GrayscaleEffect(),
    'negative': NegativeEffect(),
    'sepia': SepiaEffect(),
    'vignette': VignetteEffect(),
    'warm': WarmEffect(),
    'cool': CoolEffect(),
    'edge': EdgeDetectionEffect(),
    'posterize': PosterizeEffect(),
    'emboss': EmbossEffect(),
    'cartoon': CartoonEffect(),
    'pixelate': PixelateEffect(),
    'watercolor': WatercolorEffect(),
    'glitch': GlitchEffect(),
    'hdr': HDREffect(),
    'oilpaint': OilPaintEffect()
}

def get_effect(effect_name):
    """Get an effect instance by name"""
    return EFFECTS.get(effect_name)

def get_effect_names():
    """Get a list of all available effect names"""
    return list(EFFECTS.keys())

def apply_effect(effect_name, image, **params):
    """Apply an effect by name with additional parameters"""
    effect = get_effect(effect_name)
    if effect:
        return effect.apply(image, **params)
    return image
