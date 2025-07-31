"""
Componente Gestor de Tablas de Paquetes
Archivo: gui/components/packet_table.py
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QStackedWidget,
    QHeaderView,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config.cluster_mapping import CLUSTER_COLORS
from config.settings import MAX_PACKETS_PER_TABLE


class PacketTableManager(QWidget):
    """Gestor de tablas de paquetes (todas y solo anómalas)"""

    # Señales
    stats_updated = pyqtSignal(dict)  # Emitir estadísticas actualizadas

    def __init__(self):
        super().__init__()
        self.setup_data()
        self.setup_ui()

    def setup_data(self):
        """Inicializar datos del gestor"""
        self.total_packets = 0
        self.classification_counts = {"Normal": 0, "Anómalo": 0}
        self.current_view = "all"  # "all" o "anomalous"

    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)

        # Header con título dinámico
        self.header_layout = QHBoxLayout()
        self.status_label = QLabel("Sistema Activo - Capturando tráfico de red")
        self.status_label.setStyleSheet(
            "font-weight: bold; font-size: 18px; color: #27ae60; margin: 10px;"
        )
        self.header_layout.addWidget(self.status_label)

        # Botón de control (opcional)
        self.control_btn = QPushButton("Pausar")
        self.control_btn.setMaximumWidth(100)
        self.control_btn.clicked.connect(self.toggle_capture)
        self.header_layout.addWidget(self.control_btn)

        layout.addLayout(self.header_layout)

        # Widget apilado para alternar entre tablas
        self.stacked_widget = QStackedWidget()

        # Crear las dos tablas
        self.all_packets_table = self.create_table_widget()
        self.anomaly_packets_table = self.create_table_widget()

        # Agregar al stack
        self.stacked_widget.addWidget(self.all_packets_table)
        self.stacked_widget.addWidget(self.anomaly_packets_table)

        layout.addWidget(self.stacked_widget)

        # Referencia activa (inicialmente todos los paquetes)
        self.active_table = self.all_packets_table
        self.stacked_widget.setCurrentIndex(0)

    def create_table_widget(self):
        """Crear widget de tabla con configuración estándar"""
        table = QTableWidget(0, 8)
        table.setHorizontalHeaderLabels(
            [
                "No.",
                "Tiempo",
                "IP Origen",
                "IP Destino",
                "Protocolo",
                "Tamaño",
                "Info",
                "Clasificación",
            ]
        )

        # Configurar encabezados
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # No.
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Tiempo
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # IP Origen
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # IP Destino
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Protocolo
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Tamaño
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Info
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Clasificación

        # Estilos
        table.setAlternatingRowColors(True)
        table.setStyleSheet(
            """
            QTableWidget {
                font-size: 11px;
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
        )

        return table

    def switch_view(self, view_type):
        """Cambiar entre vista de todos los paquetes y solo anómalos"""
        self.current_view = view_type

        if view_type == "all":
            self.stacked_widget.setCurrentIndex(0)
            self.active_table = self.all_packets_table
            self.status_label.setText("Sistema Activo - Capturando tráfico de red")
            self.status_label.setStyleSheet(
                "font-weight: bold; font-size: 18px; color: #27ae60; margin: 10px;"
            )
        elif view_type == "anomalous":
            self.stacked_widget.setCurrentIndex(1)
            self.active_table = self.anomaly_packets_table
            self.status_label.setText(
                "Vista de Tráfico Anómalo - Solo paquetes sospechosos"
            )
            self.status_label.setStyleSheet(
                "font-weight: bold; font-size: 18px; color: #f44336; margin: 10px;"
            )

        # Emitir estadísticas actualizadas
        self.emit_stats()

    def add_packet(self, packet_data):
        """Agregar paquete a las tablas correspondientes"""
        # Determinar si es anómalo
        classification_str = str(packet_data[7])  # Columna de clasificación
        is_anomalous = (
            "Anómalo" in classification_str or "ANOMALO" in classification_str.upper()
        )

        # Siempre agregar a la tabla de todos los paquetes
        self.add_packet_to_table(self.all_packets_table, packet_data)

        # Solo agregar a la tabla de anómalos si es clasificado como anómalo
        if is_anomalous:
            self.add_packet_to_table(self.anomaly_packets_table, packet_data)

        # Actualizar contadores
        classification_type = "Anómalo" if is_anomalous else "Normal"
        self.classification_counts[classification_type] += 1
        self.total_packets += 1

        # Emitir estadísticas actualizadas
        self.emit_stats()

    def add_packet_to_table(self, table, packet_data):
        """Agregar paquete a una tabla específica"""
        row = table.rowCount()
        table.insertRow(row)

        for col, value in enumerate(packet_data):
            item = QTableWidgetItem(str(value))

            # Colorear filas según clasificación
            if col == 7:  # Columna de clasificación
                value_str = str(value)

                # Determinar tipo de clasificación
                classification_type = "Normal"
                if "Anómalo" in value_str or "ANOMALO" in value_str.upper():
                    classification_type = "Anómalo"

                # Aplicar colores
                if classification_type in CLUSTER_COLORS:
                    bg_color, fg_color = CLUSTER_COLORS[classification_type]
                    item.setBackground(bg_color)
                    item.setForeground(fg_color)

            table.setItem(row, col, item)

        # Mantener límite de filas para rendimiento
        max_rows = (
            MAX_PACKETS_PER_TABLE if "MAX_PACKETS_PER_TABLE" in globals() else 1000
        )
        if table.rowCount() > max_rows:
            table.removeRow(0)

        # Scroll automático a la última fila
        table.scrollToBottom()

    def emit_stats(self):
        """Emitir estadísticas actualizadas"""
        stats = {
            "total": self.total_packets,
            "classification_counts": self.classification_counts.copy(),
            "current_view": self.current_view,
            "anomaly_table_count": self.anomaly_packets_table.rowCount(),
        }
        self.stats_updated.emit(stats)

    def get_statistics(self):
        """Obtener estadísticas actuales"""
        return {
            "total_packets": self.total_packets,
            "classification_counts": self.classification_counts.copy(),
            "current_view": self.current_view,
            "anomaly_table_count": self.anomaly_packets_table.rowCount(),
            "all_table_count": self.all_packets_table.rowCount(),
        }

    def clear_tables(self):
        """Limpiar ambas tablas"""
        self.all_packets_table.setRowCount(0)
        self.anomaly_packets_table.setRowCount(0)

    def clear_stats(self):
        """Resetear estadísticas"""
        self.total_packets = 0
        self.classification_counts = {"Normal": 0, "Anómalo": 0}
        self.emit_stats()

    def toggle_capture(self):
        """Alternar pausa/continuar captura (placeholder)"""
        current_text = self.control_btn.text()
        if current_text == "Pausar":
            self.control_btn.setText("Continuar")
            self.control_btn.setStyleSheet("background-color: #ff9800;")
            # Aquí podrías emitir una señal para pausar la captura
        else:
            self.control_btn.setText("Pausar")
            self.control_btn.setStyleSheet("")
            # Aquí podrías emitir una señal para continuar la captura

    def export_current_view(self):
        """Exportar vista actual (funcionalidad futura)"""
        # Placeholder para exportar datos de la tabla actual
        table = self.active_table
        row_count = table.rowCount()
        col_count = table.columnCount()

        print(f"[INFO] Exportando {row_count} filas de la vista actual")
        # Implementar exportación a CSV, Excel, etc.

    def get_current_table(self):
        """Obtener referencia a la tabla activa"""
        return self.active_table

    def get_all_table(self):
        """Obtener referencia a la tabla de todos los paquetes"""
        return self.all_packets_table

    def get_anomaly_table(self):
        """Obtener referencia a la tabla de anómalos"""
        return self.anomaly_packets_table
