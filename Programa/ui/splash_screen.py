from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
)
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class VirtualBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)

        try:
            painter.setRenderHint(
                QPainter.RenderHint.Antialiasing
            )

            painter.fillRect(
                self.rect(),
                QColor("#060814"),
            )

            width = self.width()
            height = self.height()

            painter.setPen(
                QPen(QColor("#2D1B69"), 2.0)
            )
            painter.drawEllipse(
                int(width / 2 - 190),
                int(height / 2 - 190),
                380,
                380,
            )

            painter.setPen(
                QPen(QColor("#254E78"), 1.0)
            )
            painter.drawEllipse(
                int(width / 2 - 230),
                int(height / 2 - 230),
                460,
                460,
            )

            painter.setPen(
                QPen(QColor("#6C4DFF"), 2.0)
            )
            painter.drawArc(
                int(width / 2 - 210),
                int(height / 2 - 210),
                420,
                420,
                20 * 16,
                110 * 16,
            )

            painter.setPen(
                QPen(QColor("#1677FF"), 2.0)
            )
            painter.drawArc(
                int(width / 2 - 210),
                int(height / 2 - 210),
                420,
                420,
                200 * 16,
                100 * 16,
            )

            painter.setPen(
                QPen(QColor("#151F35"), 1.0)
            )

            spacing = 55

            for x in range(0, width, spacing):
                painter.drawLine(x, 0, x, height)

            for y in range(0, height, spacing):
                painter.drawLine(0, y, width, y)

        finally:
            painter.end()


class SplashScreen(QWidget):
    def __init__(self, on_finished):
        super().__init__()

        self.on_finished = on_finished
        self.progress_value = 0
        self.background = None

        self.setWindowTitle("VR GAMES")
        self.setMinimumSize(900, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #060814;
            }

            QLabel {
                color: white;
                background-color: transparent;
            }

            QProgressBar {
                background-color: #151A24;
                border: 1px solid #2D3748;
                border-radius: 7px;
                min-height: 14px;
                max-height: 14px;
                text-align: center;
                color: transparent;
            }

            QProgressBar::chunk {
                background-color: #6C4DFF;
                border-radius: 6px;
            }
        """)

        self.background = VirtualBackground(self)
        self.background.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self.background.setGeometry(self.rect())
        self.background.lower()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(100, 70, 100, 70)
        layout.setSpacing(16)
        layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        headset_icon = QLabel("🥽")
        headset_icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        headset_icon.setStyleSheet(
            "font-size: 100px;"
        )

        title = QLabel("VR GAMES")
        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        title.setStyleSheet("""
            font-size: 58px;
            font-weight: bold;
            color: #FFFFFF;
            letter-spacing: 5px;
        """)

        subtitle = QLabel("CONTROL CENTER")
        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        subtitle.setStyleSheet("""
            font-size: 23px;
            font-weight: bold;
            color: #A98BFF;
            letter-spacing: 8px;
        """)

        slogan = QLabel(
            "VIVE EL JUEGO. SIENTE LA REALIDAD."
        )
        slogan.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        slogan.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #6D7891;
            letter-spacing: 3px;
            margin-top: 16px;
        """)

        self.status_label = QLabel(
            "INICIANDO SISTEMA..."
        )
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.status_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #58D68D;
            letter-spacing: 2px;
            margin-top: 40px;
        """)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(420)

        layout.addStretch()
        layout.addWidget(headset_icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(slogan)
        layout.addSpacing(45)
        layout.addWidget(
            self.status_label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        layout.addWidget(
            self.progress_bar,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        layout.addStretch()

        self.opacity_effect = QGraphicsOpacityEffect(
            self
        )
        self.setGraphicsEffect(
            self.opacity_effect
        )
        self.opacity_effect.setOpacity(0.0)

        self.fade_in = QPropertyAnimation(
            self.opacity_effect,
            b"opacity",
        )
        self.fade_in.setDuration(700)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )
        self.fade_in.start()

        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(35)
        self.progress_timer.timeout.connect(
            self.update_progress
        )
        self.progress_timer.start()

        QTimer.singleShot(
            0,
            self.showMaximized,
        )

    def resizeEvent(self, event):
        if self.background is not None:
            self.background.setGeometry(
                self.rect()
            )
            self.background.lower()

        super().resizeEvent(event)

    def update_progress(self):
        self.progress_value += 1
        self.progress_bar.setValue(
            self.progress_value
        )

        if self.progress_value == 20:
            self.status_label.setText(
                "CARGANDO INTERFAZ VIRTUAL..."
            )

        elif self.progress_value == 45:
            self.status_label.setText(
                "INICIALIZANDO CONTROL DE ESTACIONES..."
            )

        elif self.progress_value == 70:
            self.status_label.setText(
                "BUSCANDO META QUEST..."
            )

        elif self.progress_value == 90:
            self.status_label.setText(
                "SISTEMA LISTO"
            )

        elif self.progress_value >= 100:
            self.progress_timer.stop()
            self.start_fade_out()

    def start_fade_out(self):
        self.fade_out = QPropertyAnimation(
            self.opacity_effect,
            b"opacity",
        )
        self.fade_out.setDuration(500)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(
            QEasingCurve.Type.InCubic
        )
        self.fade_out.finished.connect(
            self.finish_splash
        )
        self.fade_out.start()

    def finish_splash(self):
        self.hide()
        self.on_finished()
        self.deleteLater()