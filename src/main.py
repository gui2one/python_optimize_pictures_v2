from PySide6 import QtWidgets, QtCore
from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor
import sys


class MainWindow(QtWidgets.QMainWindow):
    progress = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Picture Converter")
        self.main_box = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Drop images here")

        self.main_box.addWidget(self.label)
        self.setAcceptDrops(True)
        self.setGeometry(100, 100, 700, 500)

        # progress signal
        self.progress.connect(self.on_progress)

        # Add menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        info_menu = menubar.addMenu("&Infos")
        about_action = info_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)

        self.text_output = QtWidgets.QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setTextBackgroundColor("pink")
        self.main_box.addWidget(self.text_output)

        # Create a threadpool that lives during the whole app
        self.executor = ThreadPoolExecutor(max_workers=8)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.main_box)
        self.setCentralWidget(widget)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        files = [url.toLocalFile() for url in e.mimeData().urls()]

        for f in files:
            self.executor.submit(self.worker, f, 2048)

    def worker(self, file_path, max_dim):
        """Runs inside a worker thread."""
        result = self.convert_image_file(file_path, max_dim)
        self.progress.emit(result)  # Update UI safely

    def on_progress(self, msg):
        """Runs in main thread → UI is safe."""
        self.text_output.insertHtml(
            f"<span style='font-weight: bold; color : darkgreen;'>Converted:</span> {msg}<br>"
        )

    def convert_image_file(self, file_path: str, max_dim: int = 2048):

        exts = ["png", "jpg", "jpeg", "gif", "bmp", "webp"]
        path, ext = os.path.splitext(file_path)

        if ext.replace(".", "") in exts:
            im = Image.open(file_path)
            aspect = im.size[0] / float(im.size[1])

            if aspect > 1:
                width = max_dim
                height = int(width / aspect)
            else:
                height = max_dim
                width = int(height * aspect)

            if im.size[0] > max_dim or im.size[1] > max_dim:
                im = im.resize((width, height))

            im.save(path + ".webp", "webp", quality=80)

        return f"{file_path}"

    def show_about_dialog(self):
        msg = """
Picture Converter
Version: 0.1.0
Author : gui2one
        """
        QtWidgets.QMessageBox.about(self, "About", msg)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Dark")
    window = MainWindow()
    window.setStyleSheet(
        "QTextEdit { background-color: rgb(10, 10, 10);  color : white;}"
    )
    window.show()
    app.exec()
