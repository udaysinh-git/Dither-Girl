import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import ImageEditorWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageEditorWindow()
    window.show()
    sys.exit(app.exec())