from PyQt6.QtWidgets import (QMainWindow, QLabel, QSlider, QVBoxLayout, 
                           QHBoxLayout, QWidget, QPushButton, QFileDialog, 
                           QGroupBox, QScrollArea, QSizePolicy, QFrame,
                           QSpacerItem, QGridLayout, QComboBox, QStackedWidget)
from PyQt6.QtGui import QPixmap, QImage, QAction, QCursor, QIcon, QFont
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
import cv2
import numpy as np
import copy

from ui.styles import get_dark_style
from utils.image_loader import load_image, save_image
from edit.image_filters import ImageFilters
from effects import get_effect, get_effect_names, apply_effect
from ui.components.image_view import ImageScrollArea, create_image_label
from ui.components.toolbar import EditorToolbar
from ui.components.controls_sidebar import ControlsSidebar
from ui.components.effect_manager import EffectManager

class ImageEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_filters = ImageFilters()
        self.original_image = None
        self.edited_image = None
        self.zoom_factor = 1.0
        self.edit_timer = QTimer()
        self.edit_timer.setSingleShot(True)
        self.edit_timer.timeout.connect(self.delayed_edit)
        
        # History for undo/redo
        self.history = []
        self.current_position = -1
        self.max_history = 20
        
        # Create effect manager
        self.effect_manager = EffectManager()
        
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet(get_dark_style())
        self.setWindowTitle('Dither Girl - Image Editor')
        self.setGeometry(100, 100, 1200, 800)
        self.createMenuBar()
        
        # Create main layout container
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Image view section using new component
        self.image_container = QWidget()
        self.image_container.setObjectName("image_container")
        self.image_container_layout = QVBoxLayout(self.image_container)
        self.image_container_layout.setContentsMargins(0,0,0,0)
        self.image_label = create_image_label()  # from image_view module
        self.scroll_area = ImageScrollArea()
        self.scroll_area.setWidget(self.image_container)
        self.image_container_layout.addWidget(self.image_label)
        
        # Toolbar from new module
        self.toolbar = EditorToolbar(main_window=self)
        
        image_view_layout = QVBoxLayout()
        image_view_layout.setSpacing(10)
        image_view_layout.addWidget(self.scroll_area)
        image_view_layout.addWidget(self.toolbar)
        
        # Controls sidebar from new module
        self.controls_sidebar = ControlsSidebar(main_window=self)
        
        main_layout.addLayout(image_view_layout, 3)
        main_layout.addWidget(self.controls_sidebar, 1)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def createMenuBar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Open action
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        
        # Save action
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        # Undo action
        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        # Redo action
        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
    
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", 
                                                 "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.original_image = load_image(file_path)
            self.edited_image = self.original_image.copy()
            self.display_image(self.edited_image)
            self.reset_sliders()
            self.zoom_to_fit()  # Automatically zoom to fit when opening a new image
            
            # Clear history when opening a new image
            self.clear_history()
            # Add initial state to history
            self.add_to_history()
    
    def save_image(self):
        if self.edited_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", 
                                                     "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)")
            if file_path:
                save_image(file_path, self.edited_image)
    
    def display_image(self, image):
        if image is None:
            return
            
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Create a pixmap from the image
        pixmap = QPixmap.fromImage(qt_image)
        
        # Apply zoom factor
        if self.zoom_factor != 1.0:
            new_width = int(pixmap.width() * self.zoom_factor)
            new_height = int(pixmap.height() * self.zoom_factor)
            pixmap = pixmap.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio, 
                                 Qt.TransformationMode.SmoothTransformation)
        
        # Set the pixmap to the label
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()
        
        # Update the status bar with image info and zoom level
        self.statusBar().showMessage(f"Image Size: {w}x{h} | Zoom: {int(self.zoom_factor * 100)}%")
    
    def apply_edits(self):
        if self.original_image is not None:
            # Start a timer to delay processing for smoother UI
            self.edit_timer.start(100)
    
    def delayed_edit(self):
        if self.original_image is None:
            return
        
        # Get slider values
        brightness = self.controls_sidebar.brightness_slider.value()
        contrast = self.controls_sidebar.contrast_slider.value()
        saturation = self.controls_sidebar.saturation_slider.value()
        sharpness = self.controls_sidebar.sharpness_slider.value()
        blur_amount = self.controls_sidebar.blur_slider.value()
        
        # Start with original image
        self.edited_image = self.original_image.copy()
        
        # Apply filters
        if brightness != 0:
            self.edited_image = self.image_filters.adjust_brightness(self.edited_image, brightness)
        
        if contrast != 0:
            self.edited_image = self.image_filters.adjust_contrast(self.edited_image, contrast)
        
        if saturation != 0:
            self.edited_image = self.image_filters.adjust_saturation(self.edited_image, saturation)
        
        if sharpness > 0:
            self.edited_image = self.image_filters.adjust_sharpness(self.edited_image, sharpness)
        
        if blur_amount > 0:
            self.edited_image = self.image_filters.apply_blur(self.edited_image, blur_amount)
        
        # Display the edited image
        self.display_image(self.edited_image)
        
        # Add to history after a delay to avoid adding too many states while dragging sliders
        QTimer.singleShot(500, self.add_to_history)
    
    def apply_effect_with_feedback(self, effect_func, effect_name):
        """Apply an effect with status bar feedback"""
        if self.edited_image is not None:
            self.statusBar().showMessage(f"Applying {effect_name} effect...")
            self.edited_image = effect_func(self.edited_image)
            self.display_image(self.edited_image)
            self.add_to_history()
            self.statusBar().showMessage(f"{effect_name} effect applied", 3000)
    
    def apply_effect(self, effect_name):
        """Apply an effect with parameters from sliders"""
        if self.edited_image is None:
            return
            
        self.statusBar().showMessage(f"Applying {effect_name} effect...")
        
        try:
            effect = get_effect(effect_name)
            params = {}
            
            # Get parameters from sliders if the effect has any
            if effect and effect.has_params:
                for param_name, param_data in effect.params.items():
                    slider_key = effect_name + '_' + param_name
                    if slider_key in self.controls_sidebar.effect_sliders:
                        slider_value = self.controls_sidebar.effect_sliders[slider_key].value() / 100
                        
                        # Handle parameters based on their step value
                        if param_data.get('step', 1) >= 1:
                            # Integer parameter (like levels, blur)
                            params[param_name] = int(slider_value * 100)
                        else:
                            # Floating point parameter (like intensity)
                            params[param_name] = slider_value
                            
                        # Debug message
                        print(f"Effect: {effect_name}, Param: {param_name}, Value: {params[param_name]}")
            
            # Use the effect manager to apply the effect
            self.edited_image = self.effect_manager.apply_effect(effect_name, self.edited_image, params)
            self.display_image(self.edited_image)
            self.add_to_history()
            self.statusBar().showMessage(f"{effect_name.capitalize()} effect applied", 3000)
            
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print detailed error information
            self.statusBar().showMessage(f"Error applying {effect_name} effect: {str(e)}", 5000)
    
    def reset_edits(self):
        if self.original_image is not None:
            self.edited_image = self.original_image.copy()
            self.display_image(self.edited_image)
            self.reset_sliders()
            self.add_to_history()
    
    def reset_sliders(self):
        self.controls_sidebar.brightness_slider[1].setValue(0)
        self.controls_sidebar.contrast_slider[1].setValue(0)
        self.controls_sidebar.saturation_slider[1].setValue(0)
        self.controls_sidebar.sharpness_slider[1].setValue(0)
        self.controls_sidebar.blur_slider[1].setValue(0)
    
    def zoom_in(self):
        self.zoom_factor *= 1.25
        self.update_zoom()
    
    def zoom_out(self):
        self.zoom_factor *= 0.8
        self.update_zoom()
    
    def zoom_reset(self):
        self.zoom_factor = 1.0
        self.update_zoom()
    
    def zoom_to_fit(self):
        if self.edited_image is None:
            return
            
        # Calculate zoom factor to fit the scroll area
        img_h, img_w = self.edited_image.shape[:2]
        view_w = self.scroll_area.width() - 30  # Account for scrollbars
        view_h = self.scroll_area.height() - 30
        
        # Calculate zoom to fit both width and height
        zoom_w = view_w / img_w if img_w > 0 else 1.0
        zoom_h = view_h / img_h if img_h > 0 else 1.0
        
        # Use the smaller factor to ensure entire image is visible
        self.zoom_factor = min(zoom_w, zoom_h) * 0.95  # 95% of fit to leave a small margin
        self.update_zoom()
    
    def update_zoom(self):
        # Clamp zoom factor to reasonable limits
        self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))
        
        # Redisplay image with new zoom
        if self.edited_image is not None:
            self.display_image(self.edited_image)
    
    def toggle_hand_tool(self):
        is_checked = self.toolbar.hand_tool_btn.isChecked()
        self.scroll_area.setHandMode(is_checked)
    
    def clear_history(self):
        """Clear the edit history"""
        self.history = []
        self.current_position = -1
        self.update_history_buttons()
    
    def add_to_history(self):
        """Add current state to history"""
        if self.edited_image is None:
            return
        
        # If we're not at the end of history, remove all future states
        if self.current_position < len(self.history) - 1:
            self.history = self.history[:self.current_position + 1]
        
        # Make a deep copy of the current state
        state = {
            'image': self.edited_image.copy(),
            'brightness': self.controls_sidebar.brightness_slider[1].value(),
            'contrast': self.controls_sidebar.contrast_slider[1].value(),
            'saturation': self.controls_sidebar.saturation_slider[1].value(),
            'sharpness': self.controls_sidebar.sharpness_slider[1].value(),
            'blur': self.controls_sidebar.blur_slider[1].value()
        }
        
        # Add to history
        self.history.append(state)
        self.current_position = len(self.history) - 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_position -= 1
        
        self.update_history_buttons()
    
    def update_history_buttons(self):
        """Update the enabled state of undo/redo buttons"""
        self.toolbar.undo_btn.setEnabled(self.current_position > 0)
        self.toolbar.redo_btn.setEnabled(self.current_position < len(self.history) - 1)
    
    def undo(self):
        """Go back one step in history"""
        if self.current_position > 0:
            self.current_position -= 1
            self.restore_state(self.history[self.current_position])
            self.update_history_buttons()
    
    def redo(self):
        """Go forward one step in history"""
        if self.current_position < len(self.history) - 1:
            self.current_position += 1
            self.restore_state(self.history[self.current_position])
            self.update_history_buttons()
    
    def restore_state(self, state):
        """Restore a state from history"""
        self.edited_image = state['image'].copy()
        
        # Block signals to prevent triggering edits while updating sliders
        self.controls_sidebar.brightness_slider.blockSignals(True)
        self.controls_sidebar.contrast_slider.blockSignals(True)
        self.controls_sidebar.saturation_slider.blockSignals(True)
        self.controls_sidebar.sharpness_slider.blockSignals(True)
        self.controls_sidebar.blur_slider.blockSignals(True)
        
        # Restore slider values
        self.controls_sidebar.brightness_slider.setValue(state['brightness'])
        self.controls_sidebar.contrast_slider.setValue(state['contrast'])
        self.controls_sidebar.saturation_slider.setValue(state['saturation'])
        self.controls_sidebar.sharpness_slider.setValue(state['sharpness'])
        self.controls_sidebar.blur_slider.setValue(state['blur'])
        
        # Unblock signals
        self.controls_sidebar.brightness_slider.blockSignals(False)
        self.controls_sidebar.contrast_slider.blockSignals(False)
        self.controls_sidebar.saturation_slider.blockSignals(False)
        self.controls_sidebar.sharpness_slider.blockSignals(False)
        self.controls_sidebar.blur_slider.blockSignals(False)
        
        # Display the restored image
        self.display_image(self.edited_image)
    
    def on_effect_dropdown_changed(self, index):
        """Handle effect dropdown selection with category separators"""
        # Now implemented in EffectsPanel class
        pass
