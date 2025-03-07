from PyQt6.QtWidgets import (QMainWindow, QLabel, QSlider, QVBoxLayout, 
                           QHBoxLayout, QWidget, QPushButton, QFileDialog, 
                           QGroupBox, QScrollArea, QSizePolicy, QFrame,
                           QSpacerItem)
from PyQt6.QtGui import QPixmap, QImage, QAction, QCursor, QIcon, QFont
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
import cv2
import numpy as np
import copy

from ui.styles import get_dark_style
from utils.image_loader import load_image, save_image
from edit.image_filters import ImageFilters

class ImageScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWidgetResizable(True)
        self.hand_mode = False
        self.last_pos = None
        
    def mousePressEvent(self, event):
        if self.hand_mode and event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.last_pos = event.position().toPoint()
        super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        if self.hand_mode:
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.hand_mode and self.last_pos:
            delta = event.position().toPoint() - self.last_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_pos = event.position().toPoint()
        super().mouseMoveEvent(event)
    
    def setHandMode(self, enabled):
        self.hand_mode = enabled
        if enabled:
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

class IconButton(QPushButton):
    def __init__(self, text, tooltip=None, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(40, 40)
        if tooltip:
            self.setToolTip(tooltip)
        self.setFont(QFont("Consolas", 12))

class ImageEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_filters = ImageFilters()
        self.original_image = None
        self.edited_image = None
        self.edit_timer = QTimer()
        self.edit_timer.setSingleShot(True)
        self.edit_timer.timeout.connect(self.delayed_edit)
        self.zoom_factor = 1.0
        
        # History for undo/redo
        self.history = []
        self.current_position = -1
        self.max_history = 20  # Maximum number of history states to keep
        
        self.initUI()
        
    def initUI(self):
        # Set dark theme
        self.setStyleSheet(get_dark_style())
        
        # Window properties
        self.setWindowTitle('Dither Girl - Image Editor')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.createMenuBar()
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)  # Add more spacing between main elements
        main_layout.setContentsMargins(20, 20, 20, 20)  # Add margins around the edges
        
        # Image display area
        self.image_container = QWidget()
        self.image_container.setObjectName("image_container")
        self.image_container_layout = QVBoxLayout(self.image_container)
        self.image_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel('No Image Loaded')
        self.image_label.setObjectName("image_placeholder")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Scroll area for the image
        self.scroll_area = ImageScrollArea()
        self.scroll_area.setWidget(self.image_container)
        self.image_container_layout.addWidget(self.image_label)
        self.image_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create toolbar frame
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("toolbar_frame")
        toolbar_frame.setFixedHeight(54)
        toolbar_frame.setStyleSheet("""
            #toolbar_frame {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        
        # Zoom controls
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setSpacing(6)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        
        # Undo button
        self.undo_btn = IconButton("↩", "Undo (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setEnabled(False)
        
        # Redo button
        self.redo_btn = IconButton("↪", "Redo (Ctrl+Y)")
        self.redo_btn.clicked.connect(self.redo)
        self.redo_btn.setEnabled(False)
        
        # Add a separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        separator1.setFixedWidth(1)
        separator1.setStyleSheet("background-color: #303030;")
        
        # Zoom controls
        zoom_in_btn = IconButton("+", "Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_out_btn = IconButton("-", "Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        zoom_reset_btn = IconButton("1:1", "Actual Size")
        zoom_reset_btn.clicked.connect(self.zoom_reset)
        
        zoom_fit_btn = IconButton("□", "Fit to View")
        zoom_fit_btn.clicked.connect(self.zoom_to_fit)
        
        # Add a separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setFixedWidth(1)
        separator2.setStyleSheet("background-color: #303030;")
        
        self.hand_tool_btn = IconButton("✋", "Hand Tool (Pan)")
        self.hand_tool_btn.setCheckable(True)
        self.hand_tool_btn.clicked.connect(self.toggle_hand_tool)
        
        # Add all buttons to toolbar
        toolbar_layout.addWidget(self.undo_btn)
        toolbar_layout.addWidget(self.redo_btn)
        toolbar_layout.addWidget(separator1)
        toolbar_layout.addWidget(zoom_in_btn)
        toolbar_layout.addWidget(zoom_out_btn)
        toolbar_layout.addWidget(zoom_reset_btn)
        toolbar_layout.addWidget(zoom_fit_btn)
        toolbar_layout.addWidget(separator2)
        toolbar_layout.addWidget(self.hand_tool_btn)
        toolbar_layout.addStretch()
        
        # Add zoom controls and scroll area to image view layout
        image_view_layout = QVBoxLayout()
        image_view_layout.setSpacing(10)
        image_view_layout.addWidget(self.scroll_area)
        image_view_layout.addWidget(toolbar_frame)
        
        # Controls sidebar
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(15)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Group box for editing controls
        edit_group = QGroupBox("EDITING CONTROLS")
        edit_group.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        edit_layout = QVBoxLayout(edit_group)
        edit_layout.setSpacing(16)
        
        # Slider creation helper function
        def create_slider_layout(name, min_val, max_val, default_val, connect_func):
            layout = QVBoxLayout()
            layout.setSpacing(5)
            
            # Label and value display
            header_layout = QHBoxLayout()
            label = QLabel(name)
            header_layout.addWidget(label)
            
            value_label = QLabel(f"{default_val}")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            header_layout.addWidget(value_label)
            layout.addLayout(header_layout)
            
            # Slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(default_val)
            slider.valueChanged.connect(connect_func)
            # Update value label when slider changes
            slider.valueChanged.connect(lambda v: value_label.setText(f"{v}"))
            layout.addWidget(slider)
            
            return layout, slider
        
        # Brightness slider
        brightness_layout, self.brightness_slider = create_slider_layout(
            "BRIGHTNESS", -100, 100, 0, self.apply_edits)
        edit_layout.addLayout(brightness_layout)
        
        # Contrast slider
        contrast_layout, self.contrast_slider = create_slider_layout(
            "CONTRAST", -100, 100, 0, self.apply_edits)
        edit_layout.addLayout(contrast_layout)
        
        # Saturation slider
        saturation_layout, self.saturation_slider = create_slider_layout(
            "SATURATION", -100, 100, 0, self.apply_edits)
        edit_layout.addLayout(saturation_layout)
        
        # Sharpness slider
        sharpness_layout, self.sharpness_slider = create_slider_layout(
            "SHARPNESS", 0, 100, 0, self.apply_edits)
        edit_layout.addLayout(sharpness_layout)
        
        # Blur slider
        blur_layout, self.blur_slider = create_slider_layout(
            "BLUR", 0, 30, 0, self.apply_edits)
        edit_layout.addLayout(blur_layout)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #303030;")
        edit_layout.addWidget(separator)
        
        # Effects buttons
        effects_label = QLabel("EFFECTS")
        effects_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        edit_layout.addWidget(effects_label)
        
        effects_grid = QHBoxLayout()
        
        grayscale_btn = QPushButton("Grayscale")
        grayscale_btn.clicked.connect(self.apply_grayscale)
        effects_grid.addWidget(grayscale_btn)
        
        negative_btn = QPushButton("Negative")
        negative_btn.clicked.connect(self.apply_negative)
        effects_grid.addWidget(negative_btn)
        
        edit_layout.addLayout(effects_grid)
        
        # Action buttons
        action_buttons_layout = QVBoxLayout()
        action_buttons_layout.setSpacing(10)
        
        reset_btn = QPushButton("Reset All")
        reset_btn.clicked.connect(self.reset_edits)
        action_buttons_layout.addWidget(reset_btn)
        
        save_btn = QPushButton("Save Image")
        save_btn.setObjectName("action_button")
        save_btn.clicked.connect(self.save_image)
        action_buttons_layout.addWidget(save_btn)
        
        edit_layout.addSpacing(10)
        edit_layout.addLayout(action_buttons_layout)
        
        # Add group box to sidebar
        controls_layout.addWidget(edit_group)
        controls_layout.addStretch()
        
        controls_widget.setFixedWidth(300)
        
        # Add to main layout
        main_layout.addLayout(image_view_layout, 3)
        main_layout.addWidget(controls_widget, 1)
        
        # Central widget
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
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        saturation = self.saturation_slider.value()
        sharpness = self.sharpness_slider.value()
        blur_amount = self.blur_slider.value()
        
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
    
    def apply_grayscale(self):
        if self.edited_image is not None:
            self.edited_image = self.image_filters.apply_grayscale(self.edited_image)
            self.display_image(self.edited_image)
            self.add_to_history()
    
    def apply_negative(self):
        if self.edited_image is not None:
            self.edited_image = self.image_filters.apply_negative(self.edited_image)
            self.display_image(self.edited_image)
            self.add_to_history()
    
    def reset_edits(self):
        if self.original_image is not None:
            self.edited_image = self.original_image.copy()
            self.display_image(self.edited_image)
            self.reset_sliders()
            self.add_to_history()
    
    def reset_sliders(self):
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.sharpness_slider.setValue(0)
        self.blur_slider.setValue(0)
    
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
        is_checked = self.hand_tool_btn.isChecked()
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
            'brightness': self.brightness_slider.value(),
            'contrast': self.contrast_slider.value(),
            'saturation': self.saturation_slider.value(),
            'sharpness': self.sharpness_slider.value(),
            'blur': self.blur_slider.value()
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
        self.undo_btn.setEnabled(self.current_position > 0)
        self.redo_btn.setEnabled(self.current_position < len(self.history) - 1)
    
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
        self.brightness_slider.blockSignals(True)
        self.contrast_slider.blockSignals(True)
        self.saturation_slider.blockSignals(True)
        self.sharpness_slider.blockSignals(True)
        self.blur_slider.blockSignals(True)
        
        # Restore slider values
        self.brightness_slider.setValue(state['brightness'])
        self.contrast_slider.setValue(state['contrast'])
        self.saturation_slider.setValue(state['saturation'])
        self.sharpness_slider.setValue(state['sharpness'])
        self.blur_slider.setValue(state['blur'])
        
        # Unblock signals
        self.brightness_slider.blockSignals(False)
        self.contrast_slider.blockSignals(False)
        self.saturation_slider.blockSignals(False)
        self.sharpness_slider.blockSignals(False)
        self.blur_slider.blockSignals(False)
        
        # Display the restored image
        self.display_image(self.edited_image)
