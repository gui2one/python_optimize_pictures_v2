from PySide6 import QtWidgets, QtCore
from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor


class MainWindow(QtWidgets.QMainWindow):
    progress = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Picture Converter")
        self.label = QtWidgets.QLabel("Drop images here")
        self.setCentralWidget(self.label)
        self.setAcceptDrops(True)

        self.progress.connect(self.on_progress)

        # Create a threadpool that lives during the whole app
        self.executor = ThreadPoolExecutor(max_workers=8)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        files = [url.toLocalFile() for url in e.mimeData().urls()]

        for f in files:
            self.executor.submit(self.worker, f, 800)

    def worker(self, file_path, max_dim):
        """Runs inside a worker thread."""
        result = self.convert_image_file(file_path, max_dim)
        self.progress.emit(result)  # Update UI safely

    def on_progress(self, msg):
        """Runs in main thread → UI is safe."""
        self.label.setText(msg)

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

        return f"Converted: {file_path}"


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
