#!/usr/bin/env python3
"""
Sistema de Detección de Anomalías en Red
Punto de entrada principal
"""
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    print("[INFO] Iniciando Sistema de Detección de Anomalías v2.0...")

    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        print("[OK] Interfaz gráfica iniciada correctamente")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"[ERROR] Error al iniciar la aplicación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
