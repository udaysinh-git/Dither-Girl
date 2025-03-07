from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QSlider, QPushButton, QFrame, QFileDialog)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.components.image_view import create_image_label
# Import effects panel
from ui.components.effects_panel import EffectsPanel

class ControlsSidebar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFixedWidth(300)
        self.effect_sliders = {}  # Store effect parameter sliders
        self.dropdown_to_stack_map = {}  # Map from dropdown index to stack index
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(0,0,0,0)
        
        # Create editing controls group
        self.edit_group = self.create_edit_group()
        layout.addWidget(self.edit_group)
        
        # Create effects panel
        effects_label = QLabel("EFFECTS")
        effects_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.edit_group_layout.addWidget(effects_label)
        
        # Add effects panel which contains dropdown and parameter controls
        self.effects_panel = EffectsPanel(self.main_window)
        self.edit_group_layout.addWidget(self.effects_panel)
        
        # Get references to the effect sliders and dropdown mapping
        self.effect_sliders = self.effects_panel.effect_sliders
        self.dropdown_to_stack_map = self.effects_panel.dropdown_to_stack_map
        self.effect_params_stack = self.effects_panel.effect_params_stack
        
        # Add separator after effects panel
        self.add_separator()
        
        # Add action buttons at the bottom
        self.add_action_buttons()
        
        layout.addStretch()
    
    def create_edit_group(self):
        edit_group = QGroupBox("EDITING CONTROLS")
        edit_group.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.edit_group_layout = QVBoxLayout(edit_group)
        self.edit_group_layout.setSpacing(16)
        self.create_basic_sliders()
        self.add_separator()
        return edit_group
    
    def create_basic_sliders(self):
        self.brightness_slider = self.create_slider("BRIGHTNESS", -100, 100, 0)
        self.contrast_slider = self.create_slider("CONTRAST", -100, 100, 0)
        self.saturation_slider = self.create_slider("SATURATION", -100, 100, 0)
        self.sharpness_slider = self.create_slider("SHARPNESS", 0, 100, 0)
        self.blur_slider = self.create_slider("BLUR", 0, 30, 0)
        for slider in [self.brightness_slider, self.contrast_slider,
                       self.saturation_slider, self.sharpness_slider, self.blur_slider]:
            self.edit_group_layout.addLayout(slider[0])  # slider[0] is layout
    
    def create_slider(self, name, min_val, max_val, default_val):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        header = QHBoxLayout()
        label = QLabel(name)
        header.addWidget(label)
        value_label = QLabel(str(default_val))
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(value_label)
        layout.addLayout(header)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        slider.valueChanged.connect(self.main_window.apply_edits)
        layout.addWidget(slider)
        return (layout, slider)
    
    def add_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setStyleSheet("background-color: #303030;")
        self.edit_group_layout.addWidget(sep)
    
    def add_action_buttons(self):
        btn_layout = QVBoxLayout()
        reset = QPushButton("Reset All")
        reset.clicked.connect(self.main_window.reset_edits)
        save = QPushButton("Save Image")
        save.clicked.connect(self.main_window.save_image)
        btn_layout.addWidget(reset)
        btn_layout.addWidget(save)
        self.edit_group_layout.addLayout(btn_layout)
    
    def get_slider_values(self):
        return {
            'brightness': self.brightness_slider[1].value(),
            'contrast': self.contrast_slider[1].value(),
            'saturation': self.saturation_slider[1].value(),
            'sharpness': self.sharpness_slider[1].value(),
            'blur': self.blur_slider[1].value()
        }
    
    def reset_sliders(self):
        self.brightness_slider[1].setValue(0)
        self.contrast_slider[1].setValue(0)
        self.saturation_slider[1].setValue(0)
        self.sharpness_slider[1].setValue(0)
        self.blur_slider[1].setValue(0)
    
    def restore_slider_values(self, state):
        self.brightness_slider[1].setValue(state['brightness'])
        self.contrast_slider[1].setValue(state['contrast'])
        self.saturation_slider[1].setValue(state['saturation'])
        self.sharpness_slider[1].setValue(state['sharpness'])
        self.blur_slider[1].setValue(state['blur'])
    
    def showOpenDialog(self):
        return QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
    
    def showSaveDialog(self):
        return QFileDialog.getSaveFileName(self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)")
