APP_STYLE = """
/* =========================================================
   VR GAMES CONTROL CENTER — TEMA FUTURISTA
   ========================================================= */

QWidget {
    background-color: #050816;
    color: #F5F7FF;
    font-family: "Segoe UI";
    font-size: 14px;
}

/* Ventana principal */
QMainWindow {
    background-color: #050816;
}

/* Textos */
QLabel {
    background-color: transparent;
    border: none;
    color: #F5F7FF;
}

/* Paneles generales */
QFrame {
    background-color: #0A1020;
    border: 1px solid #163A70;
    border-radius: 14px;
}

/* Botones generales */
QPushButton {
    min-height: 42px;
    padding: 7px 16px;

    color: #FFFFFF;
    background-color: #101A30;

    border: 1px solid #147DFF;
    border-radius: 8px;

    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #122849;
    border: 1px solid #00B7FF;
}

QPushButton:pressed {
    background-color: #091426;
}

QPushButton:disabled {
    color: #536078;
    background-color: #0A0F1B;
    border: 1px solid #252D3D;
}

/* Botón azul */
QPushButton[buttonType="primary"] {
    background-color: #082F70;
    border: 1px solid #00A8FF;
}

QPushButton[buttonType="primary"]:hover {
    background-color: #0A418F;
    border: 1px solid #42D4FF;
}

/* Botón magenta */
QPushButton[buttonType="danger"] {
    background-color: #531044;
    border: 1px solid #FF2BC2;
}

QPushButton[buttonType="danger"]:hover {
    background-color: #73175E;
    border: 1px solid #FF68D5;
}

/* Botón verde */
QPushButton[buttonType="success"] {
    background-color: #083E32;
    border: 1px solid #25F29A;
}

QPushButton[buttonType="success"]:hover {
    background-color: #0A5744;
    border: 1px solid #62FFBD;
}

/* Selector de juegos */
QComboBox {
    min-height: 42px;
    padding: 5px 12px;

    color: #FFFFFF;
    background-color: #0C1426;

    border: 1px solid #1F5D99;
    border-radius: 8px;

    font-size: 14px;
    font-weight: bold;
}

QComboBox:hover {
    border: 1px solid #00A8FF;
}

QComboBox::drop-down {
    width: 34px;
    border: none;
}

QComboBox QAbstractItemView {
    color: #FFFFFF;
    background-color: #0C1426;

    border: 1px solid #00A8FF;
    selection-background-color: #392272;
    selection-color: #FFFFFF;
}

/* Barra de progreso */
QProgressBar {
    min-height: 14px;
    max-height: 14px;

    color: transparent;
    background-color: #0B1220;

    border: 1px solid #1D4D83;
    border-radius: 7px;
}

QProgressBar::chunk {
    background-color: #147DFF;
    border-radius: 6px;
}

/* Área desplazable */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    width: 10px;
    margin: 3px;
    background-color: #080D18;
}

QScrollBar::handle:vertical {
    min-height: 30px;
    background-color: #1A5D9B;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00A8FF;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

/* Diálogos */
QDialog {
    background-color: #050816;
}

/* Ventanas emergentes */
QMessageBox {
    background-color: #080D18;
}

QMessageBox QLabel {
    color: #FFFFFF;
    font-size: 14px;
}
"""


COLORS = {
    "background": "#050816",
    "panel": "#0A1020",
    "panel_secondary": "#0C1426",

    "blue": "#00A8FF",
    "blue_dark": "#147DFF",

    "magenta": "#FF2BC2",
    "purple": "#A66CFF",

    "green": "#25F29A",
    "yellow": "#F6C945",
    "red": "#FF4E6D",

    "text": "#F5F7FF",
    "muted": "#8290A8",
    "border": "#163A70",
}