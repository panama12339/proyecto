"""Estilos CSS para la aplicación"""

MAIN_STYLESHEET = """
QWidget {
    background-color: #f0f0f0;
}
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #45a049;
}
QPushButton.selected {
    background-color: #2196F3;
}
QPushButton.anomaly {
    background-color: #f44336;
}
QPushButton.anomaly:hover {
    background-color: #d32f2f;
}
QTableWidget {
    background-color: white;
    alternate-background-color: #f9f9f9;
    selection-background-color: #007acc;
    gridline-color: #d0d0d0;
}
QHeaderView::section {
    background-color: #e0e0e0;
    padding: 8px;
    font-weight: bold;
    border: 1px solid #d0d0d0;
}
"""
