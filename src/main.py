import PySide6.QtWidgets
from PIL import Image
import os
from multiprocessing.pool import ThreadPool


def convert_image_file(file_path: str, max_dim: int = 2048):

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


class MainWindow(PySide6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Picture Converter")
        self.label = PySide6.QtWidgets.QLabel("Hello World")
        self.setCentralWidget(self.label)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):

        with ThreadPool(8) as p:
            files = [url.toLocalFile() for url in e.mimeData().urls()]
            p.starmap(convert_image_file, [(file, 800) for file in files])


if __name__ == "__main__":
    app = PySide6.QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
