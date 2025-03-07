from PyQt6.QtWidgets import QScrollArea, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

class ImageScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
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

def create_image_label():
    label = QLabel("No Image Loaded")
    label.setObjectName("image_placeholder")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return label
