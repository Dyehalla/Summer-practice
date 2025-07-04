import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget, QFileDialog,
                             QMessageBox, QLabel, QDialog,
                             QInputDialog, QHBoxLayout, QLineEdit,
                             QComboBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
from image_pick_window import ImageDialog
import numpy as np

"""Главное окно приложения с изображением и функциями"""
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stupid Image Processor")
        self.setGeometry(100, 100, 800, 700)

        # Основные элементы интерфейса
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0;")

        self.btn_change = QPushButton("Сменить изображение")
        self.btn_change.clicked.connect(self.change_image)

        self.btn_save = QPushButton("Сохранить изображение")
        self.btn_save.clicked.connect(self.save_image)

        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["Все каналы", "Красный канал", "Зеленый канал", "Синий канал"])
        self.channel_combo.currentIndexChanged.connect(self.show_color_channel)

        self.btn_func1 = QPushButton("1. Обрезать изображение")
        self.btn_func1.clicked.connect(self.crop_image)

        self.btn_func2 = QPushButton("2. Повысить яркость")
        self.btn_func2.clicked.connect(self.increase_brightness)

        self.btn_func3 = QPushButton("3. Нарисовать круг")
        self.btn_func3.clicked.connect(self.draw_circle)

        # Расположение элементов
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label, 1)
        layout.addWidget(self.btn_change)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.channel_combo)
        layout.addWidget(self.btn_func1)
        layout.addWidget(self.btn_func2)
        layout.addWidget(self.btn_func3)

        central_widget.setLayout(layout)

        # Текущее изображение
        self.current_image_path = None
        self.original_image = None
        self.processed_image = None
        self.show_placeholder()

    """Показ плейсхолдера при отсутствии изображения"""
    def show_placeholder(self):
        self.image_label.setText("Выберите изображение")
        self.image_label.setStyleSheet("color: #888; font-size: 16px;")
        self.disable_functions()

    """Активация кнопок функций"""
    def enable_functions(self):
        self.btn_func1.setEnabled(True)
        self.btn_func2.setEnabled(True)
        self.btn_func3.setEnabled(True)
        self.channel_combo.setEnabled(True)
        self.btn_save.setEnabled(True)

    """Деактивация кнопок функций"""
    def disable_functions(self):
        self.btn_func1.setEnabled(False)
        self.btn_func2.setEnabled(False)
        self.btn_func3.setEnabled(False)
        self.channel_combo.setEnabled(False)
        self.btn_save.setEnabled(False)

    """Открытие диалога для смены изображения"""
    def change_image(self):
        dialog = ImageDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.current_image_path = dialog.image_path
            self.original_image = cv2.imread(self.current_image_path)
            self.processed_image = self.original_image.copy()
            self.load_image()
            self.channel_combo.setCurrentIndex(0)

    """Сохранение обработанного изображения"""
    def save_image(self):
        if self.processed_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить изображение", "",
                "Images (*.png *.jpg *.jpeg *.bmp)"
            )
            if file_path:
                cv2.imwrite(file_path, self.processed_image)
                QMessageBox.information(self, "Сохранено", "Изображение успешно сохранено")

    """Загрузка и отображение изображения"""
    def load_image(self, image=None):
        if image is None:
            image = self.processed_image

        if image is not None:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)

            scaled_pixmap = pixmap.scaled(
                self.image_label.width() - 20,
                self.image_label.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setText("")
            self.image_label.setStyleSheet("background-color: none;")
            self.enable_functions()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
            self.show_placeholder()

    """Отображение выбранного цветового канала"""
    def show_color_channel(self, index):
        if self.processed_image is None:
            return

        if index == 0:  # Все каналы
            self.load_image(self.processed_image)
        else:
            # Создаем копию для отображения канала
            display_image = self.processed_image.copy()

            if index == 1:  # Красный канал
                display_image[:, :, 0] = 0  # Убираем синий
                display_image[:, :, 1] = 0  # Убираем зеленый
            elif index == 2:  # Зеленый канал
                display_image[:, :, 0] = 0  # Убираем синий
                display_image[:, :, 2] = 0  # Убираем красный
            elif index == 3:  # Синий канал
                display_image[:, :, 1] = 0  # Убираем зеленый
                display_image[:, :, 2] = 0  # Убираем красный

            self.load_image(display_image)

    """Обработчик изменения размера окна"""
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.processed_image is not None:
            self.load_image()

    """Обрезка изображения по заданным координатам"""
    def crop_image(self):
        if self.processed_image is None:
            return

        # Получаем размеры изображения
        h, w = self.processed_image.shape[:2]

        # Диалог для ввода координат
        dialog = QDialog(self)
        dialog.setWindowTitle("Введите координаты обрезки")
        layout = QVBoxLayout()

        # Поля для ввода
        inputs = []
        labels = ["Верхняя граница (Y1):", "Левая граница (X1):",
                  "Нижняя граница (Y2):", "Правая граница (X2):"]
        default_values = [0, 0, h, w]

        for i in range(4):
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(labels[i]))
            line_edit = QLineEdit(str(default_values[i]))
            inputs.append(line_edit)
            hbox.addWidget(line_edit)
            layout.addLayout(hbox)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            try:
                y1 = int(inputs[0].text())
                x1 = int(inputs[1].text())
                y2 = int(inputs[2].text())
                x2 = int(inputs[3].text())

                # Проверка корректности координат
                if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0 or x2 > w or y2 > h:
                    raise ValueError("Некорректные координаты обрезки")

                # Выполняем обрезку
                self.processed_image = self.processed_image[y1:y2, x1:x2]
                self.load_image()
                self.channel_combo.setCurrentIndex(0)

            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при обрезке: {str(e)}")

    """Повышение яркости изображения"""
    def increase_brightness(self):
        if self.processed_image is None:
            return

        # Получаем процент увеличения яркости от пользователя
        percent, ok = QInputDialog.getInt(
            self, "Повышение яркости",
            "Введите процент увеличения яркости (1-1000%):",
            0, 1, 1000  # по умолчанию 0%, минимум 1%, максимум 1000%
        )

        if ok:
            try:
                # Преобразуем в HSV
                hsv = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)

                v = v.astype('float32')
                v = v * (1 + percent / 100.0)
                v = np.clip(v, 0, 255)
                v = v.astype('uint8')

                # Собираем изображение обратно
                final_hsv = cv2.merge((h, s, v))
                self.processed_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

                self.load_image()
                self.channel_combo.setCurrentIndex(0)

            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при изменении яркости: {str(e)}")

    """Рисование круга на изображении"""
    def draw_circle(self):
        if self.processed_image is None:
            return

        # Диалог для ввода параметров круга
        dialog = QDialog(self)
        dialog.setWindowTitle("Параметры круга")
        layout = QVBoxLayout()

        # Поля для ввода
        inputs = []
        labels = ["Центр X:", "Центр Y:", "Радиус:"]

        for label in labels:
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(label))
            line_edit = QLineEdit()
            inputs.append(line_edit)
            hbox.addWidget(line_edit)
            layout.addLayout(hbox)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            try:
                center_x = int(inputs[0].text())
                center_y = int(inputs[1].text())
                radius = int(inputs[2].text())

                # Рисуем красный круг на копии изображения
                img_with_circle = self.processed_image.copy()
                cv2.circle(img_with_circle, (center_x, center_y), radius, (0, 0, 255), 2)

                self.processed_image = img_with_circle
                self.load_image()
                self.channel_combo.setCurrentIndex(0)

            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при рисовании круга: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())