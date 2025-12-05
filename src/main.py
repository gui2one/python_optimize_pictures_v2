from PySide6 import QtWidgets, QtCore, QtGui
from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor
import sys

styles = """
MainWindow[dragActive="true"]{
    background-color : orange;
}
QTextEdit { background-color: rgb(10, 10, 10);  color : white;}
QLabel#drop_label{
    font-size : 20px;
    color : black;
}
"""


def load_version_string():
    with open("app_version.txt", "r") as f:
        return f.read().strip()


class DimensionSelector(QtWidgets.QWidget):
    min_val: int
    max_val: int
    cur_val: int
    val_changed = QtCore.Signal(int)

    def __init__(
        self,
        parent=None,
        start_val=2048,
        max_val=8096,
        min_val=16,
        label: str = "No label !!!",
    ):
        super().__init__(parent)

        self.max_val = max_val
        self.min_val = min_val
        self.cur_val = start_val
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.dim_input = QtWidgets.QLineEdit(str(self.cur_val), maxLength=4)
        self.dim_input.setFixedWidth(100)
        self.layout.addWidget(self.dim_input)
        self.dim_input.setValidator(QtGui.QIntValidator(self.min_val, self.max_val))
        self.dim_input.textChanged.connect(self.set_value)

        self.label = QtWidgets.QLabel(label)
        self.layout.addWidget(self.label)

    def set_value(self, value):
        self.cur_val = int(value)
        self.val_changed.emit(self.cur_val)


class SliderWidget(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)

    def __init__(self, parent=None, label: str = "No label !!!"):
        super().__init__(parent)
        self.main_box = QtWidgets.QVBoxLayout()
        self.main_box.setContentsMargins(0, 0, 0, 0)

        self.hbox = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel(label)
        self.main_box.addWidget(self.label)

        self.setLayout(self.main_box)

        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setFixedWidth(200)
        self.slider.setRange(20, 100)
        self.slider.setValue(80)
        self.slider.valueChanged.connect(self.set_value)
        self.hbox.addWidget(self.slider)

        self.value_label = QtWidgets.QLabel(str(self.slider.value()))
        self.hbox.addWidget(self.value_label)
        self.main_box.addLayout(self.hbox)

    def set_value(self, value):
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)


class FormatSelector(QtWidgets.QWidget):
    val_changed = QtCore.Signal(int)

    def __init__(self, parent=None, items: list[str] = ["jpg", "webp"]):
        super().__init__(parent)
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.hbox)
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(items)
        self.combo.setFixedWidth(100)
        self.combo.currentIndexChanged.connect(self.on_format_changed)
        self.hbox.addWidget(self.combo)

        self.label = QtWidgets.QLabel("Export Format")
        self.hbox.addWidget(self.label)

    def add_items(self, items: list[str]):
        self.combo.addItems(items)

    def on_format_changed(self, index):
        self.val_changed.emit(index)


def Separator():
    frame = QtWidgets.QFrame()
    frame.setFrameShape(QtWidgets.QFrame.HLine)
    frame.setFrameShadow(QtWidgets.QFrame.Raised)
    frame.setContentsMargins(0, 0, 0, 0)
    return frame


class MainWindow(QtWidgets.QMainWindow):
    progress = QtCore.Signal(str)

    max_dim: int = 2048
    comp_level: int = 80
    export_formats = ["webp", "jpeg"]
    export_format_selected: str

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Picture Optimizer")
        self.setWindowIcon(QtGui.QIcon("res/picture_optimizer.ico"))
        self.setAcceptDrops(True)
        self.setGeometry(100, 100, 700, 600)

        self.export_format_selected = self.export_formats[0]
        self.main_box = QtWidgets.QVBoxLayout()
        self.params_box = QtWidgets.QVBoxLayout()
        self.top_hbox = QtWidgets.QHBoxLayout()
        self.top_hbox.addLayout(self.params_box)
        self.main_box.addLayout(self.top_hbox)
        self.dim_selector = DimensionSelector(
            self,
            min_val=16,
            max_val=8096,
            start_val=self.max_dim,
            label="Max Dimension",
        )
        self.dim_selector.val_changed.connect(self.on_max_dim_changed)
        self.params_box.addWidget(self.dim_selector)

        separator = Separator()
        self.params_box.addWidget(separator)

        self.comp_level_selector2 = SliderWidget(self, label="Compression Level")
        self.comp_level_selector2.valueChanged.connect(self.on_comp_level_changed)
        self.params_box.addWidget(self.comp_level_selector2)

        separator = Separator()
        self.params_box.addWidget(separator)

        self.format_selector = FormatSelector(self, self.export_formats)
        self.format_selector.val_changed.connect(self.on_format_changed)
        self.params_box.addWidget(self.format_selector)

        separator = Separator()
        self.params_box.addWidget(separator)

        self.label = QtWidgets.QLabel("Drop images here")
        self.label.setObjectName("drop_label")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFixedSize(400, 100)

        self.top_hbox.addWidget(self.label)

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

    def on_max_dim_changed(self, max_dim):
        self.max_dim = max_dim

    def on_comp_level_changed(self, comp_level):
        self.comp_level = comp_level

    def on_format_changed(self, index):

        self.export_format_selected = self.export_formats[index]
        # print("format changed", self.export_format_selected)

    def dragEnterEvent(self, e):
        self.setProperty("dragActive", "true")
        e.accept()
        self.style().unpolish(self)
        self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("dragActive", "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, e):
        self.setProperty("dragActive", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        files = [url.toLocalFile() for url in e.mimeData().urls()]

        for f in files:
            # print(self.export_format_selected)
            self.executor.submit(
                self.worker,
                f,
                self.max_dim,
                self.export_format_selected,
                self.comp_level,
            )

    def worker(
        self,
        file_path,
        max_dim,
        format,
        comp_level=80,
    ):
        # print("worker starting ....")
        """Runs inside a worker thread."""
        result = self.convert_image_file(file_path, max_dim, comp_level, format=format)

        self.progress.emit(result)  # Update UI safely

    def on_progress(self, msg):
        """Runs in main thread → UI is safe."""
        if msg == "":
            self.text_output.insertHtml(
                f"<span style='font-weight: bold; color : white; background-color:red;'>Unsupported File Format</span><br>"
            )
            return

        self.text_output.insertHtml(
            f"<span style='font-weight: bold; color : darkgreen;'>Converted:</span> {msg}<br>"
        )
        self.text_output.moveCursor(QtGui.QTextCursor.End)

    def convert_image_file(
        self, file_path: str, max_dim: int = 2048, comp_level: int = 80, format="webp"
    ):
        exts = ["png", "jpg", "jpeg", "gif", "bmp", "webp"]
        path, ext = os.path.splitext(file_path)

        if ext.replace(".", "").lower() in exts:

            im = Image.open(file_path)
            aspect = im.size[0] / float(im.size[1])

            if im.mode in ("RGBA", "P") and format == "jpeg":
                im = im.convert("RGB")

            if aspect > 1:
                width = max_dim
                height = int(width / aspect)
            else:
                height = max_dim
                width = int(height * aspect)

            if im.size[0] > max_dim or im.size[1] > max_dim:
                im = im.resize((width, height))

            new_path = path + "_OPTIMIZED." + format
            # print("new_path : ", new_path)
            try:
                im.save(new_path, quality=comp_level, optimize=True, format=format)
            except Exception as e:
                print(e)

            return new_path
        return ""

    def show_about_dialog(self):
        msg = f"""
Picture Converter
Version: {load_version_string()}
Author : gui2one
        """
        QtWidgets.QMessageBox.about(self, "About", msg)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Dark")
    window = MainWindow()
    window.setStyleSheet(styles)
    window.show()
    app.exec()
