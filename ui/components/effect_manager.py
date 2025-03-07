from effects import get_effect, apply_effect

class EffectManager:
    def __init__(self):
        pass
        
    def apply_effect(self, effect_name, image, params=None):
        if params is None:
            params = {}
        effect = get_effect(effect_name)
        if effect:
            return effect.apply(image, **params)
        return image
