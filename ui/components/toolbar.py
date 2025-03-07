from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class IconButton(QPushButton):
    def __init__(self, text, tooltip=None, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(40, 40)
        if tooltip:
            self.setToolTip(tooltip)
        self.setFont(QFont("Consolas", 12))

class EditorToolbar(QFrame):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setObjectName("toolbar_frame")
        self.setFixedHeight(54)
        self.setStyleSheet("""
            #toolbar_frame {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        self.init_toolbar()
        
    def init_toolbar(self):
        toolbar_layout = QHBoxLayout(self)
        toolbar_layout.setSpacing(6)
        toolbar_layout.setContentsMargins(8,4,8,4)
        
        self.undo_btn = IconButton("↩", "Undo (Ctrl+Z)")
        self.undo_btn.clicked.connect(self.main_window.undo)
        self.undo_btn.setEnabled(False)
        
        self.redo_btn = IconButton("↪", "Redo (Ctrl+Y)")
        self.redo_btn.clicked.connect(self.main_window.redo)
        self.redo_btn.setEnabled(False)
        
        # ...existing code for separators, zoom buttons, hand tool...
        zoom_in_btn = IconButton("+", "Zoom In")
        zoom_in_btn.clicked.connect(self.main_window.zoom_in)
        zoom_out_btn = IconButton("-", "Zoom Out")
        zoom_out_btn.clicked.connect(self.main_window.zoom_out)
        zoom_reset_btn = IconButton("1:1", "Actual Size")
        zoom_reset_btn.clicked.connect(self.main_window.zoom_reset)
        zoom_fit_btn = IconButton("□", "Fit to View")
        zoom_fit_btn.clicked.connect(self.main_window.zoom_to_fit)
        
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        separator1.setFixedWidth(1)
        separator1.setStyleSheet("background-color: #303030;")
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setFixedWidth(1)
        separator2.setStyleSheet("background-color: #303030;")
        
        self.hand_tool_btn = IconButton("✋", "Hand Tool (Pan)")
        self.hand_tool_btn.setCheckable(True)
        self.hand_tool_btn.clicked.connect(lambda checked: self.main_window.toggle_hand_tool(checked))
        
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
        
    def set_undo_enabled(self, enabled):
        self.undo_btn.setEnabled(enabled)
        
    def set_redo_enabled(self, enabled):
        self.redo_btn.setEnabled(enabled)
