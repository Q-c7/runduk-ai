import os

from PyQt6.QtCore import QFile
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for img in os.listdir(script_dir):
        if not img.endswith(".png"):
            continue
        pixmap = QPixmap()
        pixmap.load(img)
        file = QFile(img)
        pixmap.save(file, "PNG")


if __name__ == "__main__":
    app = QApplication([])
    main()
