"""Mapeo de clusters y colores"""

from PyQt5.QtCore import Qt

# Mapeo de clusters a categorías
CLUSTER_MAPPING = {
    0: "Anómalo",
    1: "Normal",
    2: "Anómalo",
}

# Colores para la interfaz
CLUSTER_COLORS = {"Anómalo": (Qt.red, Qt.white), "Normal": (Qt.green, Qt.white)}
