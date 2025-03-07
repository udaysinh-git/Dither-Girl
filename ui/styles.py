def get_dark_style():
    return """
        * {
            font-family: 'Consolas', 'Courier New', monospace;
        }
        
        QMainWindow {
            background-color: #121212;
            color: #f0f0f0;
        }
        
        QLabel {
            color: #f0f0f0;
            font-size: 11px;
            letter-spacing: 0.5px;
        }
        
        QLabel#image_placeholder {
            color: #757575;
            font-size: 14px;
            font-weight: bold;
        }
        
        QGroupBox {
            background-color: #1e1e1e;
            border: 1px solid #303030;
            border-radius: 10px;
            margin-top: 1.5ex;
            color: #f0f0f0;
            padding: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 8px;
            background-color: #1e1e1e;
        }
        
        QSlider::groove:horizontal {
            border: none;
            height: 4px;
            background: #424242;
            margin: 2px 0;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background: #e0e0e0;
            border: none;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #ffffff;
        }
        
        QPushButton {
            background-color: #2d2d2d;
            color: #ffffff;
            border: none;
            padding: 8px;
            border-radius: 6px;
            font-weight: bold;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-size: 10px;
        }
        
        QPushButton:hover {
            background-color: #424242;
        }
        
        QPushButton:pressed {
            background-color: #505050;
        }
        
        QPushButton:checked {
            background-color: #bb86fc;
            color: #121212;
        }
        
        QPushButton:disabled {
            background-color: #1d1d1d;
            color: #555555;
        }
        
        QPushButton#action_button {
            background-color: #bb86fc;
            color: #121212;
        }
        
        QPushButton#action_button:hover {
            background-color: #d0a8ff;
        }
        
        QPushButton#action_button:pressed {
            background-color: #a076dd;
        }
        
        QScrollArea {
            border: none;
            background-color: #121212;
        }
        
        QScrollBar:vertical {
            border: none;
            background-color: #1e1e1e;
            width: 10px;
            margin: 0px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #424242;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #626262;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #1e1e1e;
            height: 10px;
            margin: 0px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #424242;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #626262;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        QMenuBar {
            background-color: #121212;
            color: #f0f0f0;
            border-bottom: 1px solid #303030;
            font-size: 11px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
        }
        
        QMenuBar::item:selected {
            background-color: #2d2d2d;
            border-radius: 4px;
        }
        
        QMenu {
            background-color: #1e1e1e;
            color: #f0f0f0;
            border: 1px solid #303030;
            border-radius: 6px;
            padding: 4px 0px;
        }
        
        QMenu::item {
            padding: 6px 32px 6px 20px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #2d2d2d;
        }
        
        QStatusBar {
            background-color: #1e1e1e;
            color: #b0b0b0;
            border-top: 1px solid #303030;
            font-size: 10px;
        }
        
        QToolTip {
            border: 1px solid #303030;
            padding: 4px;
            border-radius: 2px;
            opacity: 200;
            background-color: #1e1e1e;
            color: #f0f0f0;
            font-size: 10px;
        }
    """
