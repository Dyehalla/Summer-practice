import cv2
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QPushButton, QFileDialog, QMessageBox


class ImageDialog(QDialog):
    """Диалоговое окно для выбора источника изображения"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор изображения")
        self.setGeometry(150, 150, 300, 150)

        layout = QVBoxLayout()

        self.btn_select = QPushButton("Выбрать из файла", self)
        self.btn_select.clicked.connect(self.select_image)

        self.btn_camera = QPushButton("Сделать фото с камеры", self)
        self.btn_camera.clicked.connect(self.capture_from_camera)

        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_camera)
        self.setLayout(layout)

        self.image_path = None
        self.camera = None

    def select_image(self):
        """Выбор изображения через проводник"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.image_path = file_path
            self.accept()

    def capture_from_camera(self):
        """Захват изображения с вебкамеры"""
        try:
            self.camera = cv2.VideoCapture(0)

            if not self.camera.isOpened():
                raise Exception("Не удалось открыть камеру")

            ret, frame = self.camera.read()
            if not ret:
                raise Exception("Не удалось получить кадр с камеры")

            self.image_path = "webcam_capture.jpg"
            cv2.imwrite(self.image_path, frame)
            self.accept()

        except Exception as e:
            self.show_error_message(str(e))

        finally:
            if self.camera is not None:
                self.camera.release()

    def show_error_message(self, error):
        """Показ сообщения об ошибке"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Ошибка камеры")
        msg.setText("Не удалось сделать фото с вебкамеры")

        possible_causes = [
            "Камера не подключена или неисправна",
            "Другое приложение использует камеру",
            "Нет разрешения на доступ к камере",
            "Драйверы камеры не установлены",
            f"\nТехническая информация:\n{error}"
        ]

        msg.setDetailedText("\n".join(possible_causes))
        msg.exec_()