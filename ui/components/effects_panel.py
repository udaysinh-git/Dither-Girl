from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QStackedWidget, QSlider)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from effects import get_effect, get_effect_names

class EffectsPanel(QWidget):
    """Panel for selecting and configuring image effects"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.effect_sliders = {}  # Track sliders for effect parameters
        self.dropdown_to_stack_map = {}  # Map dropdown indices to stack indices
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # Effects dropdown with category labels
        dropdown_layout = QHBoxLayout()
        dropdown_label = QLabel("Effect:")
        self.effects_dropdown = QComboBox()
        self.effects_dropdown.addItem("Select an effect...")
        
        # Updated categories with all effects properly organized
        effect_categories = {
            "Basic": ["grayscale", "negative", "posterize"],
            "Color": ["sepia", "warm", "cool"],
            "Artistic": ["cartoon", "watercolor", "oilpaint", "emboss"],
            "Stylistic": ["vignette", "edge", "pixelate", "glitch"],
            "Advanced": ["hdr"]
        }
        
        # Add separator after "Select an effect..."
        self.effects_dropdown.insertSeparator(1)
        
        # Add all effects by category
        for category, effect_list in effect_categories.items():
            self.effects_dropdown.addItem(f"--- {category} ---")
            self.effects_dropdown.model().item(self.effects_dropdown.count() - 1).setEnabled(False)
            
            for effect_name in effect_list:
                effect = get_effect(effect_name)
                if effect:
                    self.effects_dropdown.addItem(effect.name)
            
            # Add separator after each category except the last
            if category != list(effect_categories.keys())[-1]:
                self.effects_dropdown.insertSeparator(self.effects_dropdown.count())
        
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.effects_dropdown)
        layout.addLayout(dropdown_layout)
        
        # Effect parameter sliders stack
        self.effect_params_stack = QStackedWidget()
        
        # Empty widget for "Select an effect..." and separators
        empty_widget = QWidget()
        self.effect_params_stack.addWidget(empty_widget)
        
        # Track mapping from dropdown index to stack widget index
        self.dropdown_to_stack_map = {0: 0}  # "Select an effect..." maps to empty widget
        stack_idx = 1
        
        # Create UI for each effect
        all_effect_names = get_effect_names()
        
        # Add effect widgets to the stack
        for effect_name in all_effect_names:
            effect = get_effect(effect_name)
            if not effect:
                continue
                
            effect_widget = QWidget()
            effect_layout = QVBoxLayout(effect_widget)
            
            # Add effect description
            effect_info = QLabel(effect.description)
            effect_info.setWordWrap(True)
            effect_layout.addWidget(effect_info)
            
            # Add parameter sliders if the effect has parameters
            if effect.has_params:
                for param_name, param_data in effect.params.items():
                    param_layout = QVBoxLayout()
                    param_header = QHBoxLayout()
                    
                    # Parameter label and value display
                    display_value = param_data['default']
                    if param_data.get('step', 1) < 1:  # Format floating point values
                        param_label = QLabel(f"{param_data['label']}: {display_value:.2f}")
                    else:  # Format integer values
                        param_label = QLabel(f"{param_data['label']}: {int(display_value)}")
                        
                    param_header.addWidget(param_label)
                    param_layout.addLayout(param_header)
                    
                    # Create slider for parameter
                    slider = QSlider(Qt.Orientation.Horizontal)
                    slider.setRange(
                        int(param_data['min'] * 100),
                        int(param_data['max'] * 100)
                    )
                    slider.setValue(int(param_data['default'] * 100))
                    
                    # Store reference to param_label for updating it
                    slider.param_label = param_label
                    slider.param_name = param_data['label']
                    slider.is_float = param_data.get('step', 1) < 1
                    
                    # Connect value change handler based on parameter type
                    slider.valueChanged.connect(self.create_slider_value_handler(slider))
                    
                    param_layout.addWidget(slider)
                    effect_layout.addLayout(param_layout)
                    self.effect_sliders[effect_name + '_' + param_name] = slider
            
            # Apply button
            apply_button = QPushButton(f"Apply {effect.name}")
            # Store effect_name separately to avoid lambda closure issues
            apply_button.effect_name = effect_name 
            apply_button.clicked.connect(
                lambda checked=False, effect_name=effect_name: 
                self.main_window.apply_effect(effect_name)
            )
            effect_layout.addWidget(apply_button)
            
            # Spacer at the bottom
            effect_layout.addStretch()
            
            # Add the widget to stack
            self.effect_params_stack.addWidget(effect_widget)
            
            # Find where this effect appears in the dropdown
            for i in range(self.effects_dropdown.count()):
                if self.effects_dropdown.itemText(i) == effect.name:
                    self.dropdown_to_stack_map[i] = stack_idx
                    break
            
            stack_idx += 1
        
        # Connect dropdown to handle changes
        self.effects_dropdown.currentIndexChanged.connect(self.on_effect_dropdown_changed)
        
        # Add effect controls to layout
        layout.addWidget(self.effect_params_stack)
    
    def create_slider_value_handler(self, slider):
        """Create a value changed handler for a parameter slider"""
        if slider.is_float:
            return lambda v: slider.param_label.setText(f"{slider.param_name}: {v/100:.2f}")
        else:
            return lambda v: slider.param_label.setText(f"{slider.param_name}: {int(v/100)}")
    
    def on_effect_dropdown_changed(self, index):
        """Handle effect dropdown selection with category separators"""
        # Check if this index is in our mapping
        if index in self.dropdown_to_stack_map:
            self.effect_params_stack.setCurrentIndex(self.dropdown_to_stack_map[index])
        else:
            # This is a category label or separator - select the empty widget
            self.effect_params_stack.setCurrentIndex(0)
