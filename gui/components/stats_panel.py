"""
Componente Panel de Estadísticas
Archivo: gui/components/stats_panel.py
"""

import time
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class StatsPanel(QWidget):
    """Panel de estadísticas del sistema"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.reset_stats()

    def setup_ui(self):
        """Configurar interfaz del panel"""
        layout = QVBoxLayout(self)

        # Título del panel
        title = QLabel("Estadísticas del Sistema")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px; padding: 5px;")
        layout.addWidget(title)

        # Label principal de estadísticas
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignLeft)
        self.stats_label.setStyleSheet(
            """
            QLabel {
                margin: 10px;
                padding: 15px;
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                line-height: 1.4;
                font-size: 11px;
            }
        """
        )
        layout.addWidget(self.stats_label)

        # Información del modelo
        self.model_info_label = QLabel()
        self.model_info_label.setAlignment(Qt.AlignLeft)
        self.model_info_label.setStyleSheet(
            """
            QLabel {
                margin: 5px 10px;
                padding: 10px;
                background-color: #e8f5e8;
                border-radius: 6px;
                border: 1px solid #c8e6c9;
                font-size: 10px;
                color: #2e7d32;
            }
        """
        )
        layout.addWidget(self.model_info_label)

        # Inicializar contenido
        self.update_model_info("K-Means", 3, 2, "Activo")
        self.update_stats(0, {"Normal": 0, "Anómalo": 0}, "all")

    def reset_stats(self):
        """Resetear estadísticas"""
        self.total_packets = 0
        self.classification_counts = {"Normal": 0, "Anómalo": 0}
        self.current_view = "all"

    def update_stats(
        self, total_packets, classification_counts, current_view, anomaly_table_count=0
    ):
        """Actualizar estadísticas mostradas"""
        self.total_packets = total_packets
        self.classification_counts = classification_counts
        self.current_view = current_view

        # Calcular porcentajes
        normal_count = classification_counts.get("Normal", 0)
        anomalo_count = classification_counts.get("Anómalo", 0)

        normal_pct = (normal_count / max(1, total_packets)) * 100
        anomalo_pct = (anomalo_count / max(1, total_packets)) * 100

        # Preparar texto según la vista actual
        if current_view == "anomalous":
            stats_text = f"""📊 Vista Anómalos:
            
🔴 Anómalos mostrados: {anomaly_table_count}
📦 Total capturados: {total_packets}

📈 Porcentajes:
  • Anómalos: {anomalo_pct:.1f}%
  • Normales: {normal_pct:.1f}%

⏰ Tiempo: {time.strftime('%H:%M:%S')}
🔄 Actualizado: Cada segundo"""
        else:
            stats_text = f"""📊 Estadísticas Generales:

📦 Total paquetes: {total_packets}

📈 Clasificación:
  • 🟢 Normales: {normal_count} ({normal_pct:.1f}%)
  • 🔴 Anómalos: {anomalo_count} ({anomalo_pct:.1f}%)

⏰ Tiempo: {time.strftime('%H:%M:%S')}
🔄 Estado: Capturando..."""

        self.stats_label.setText(stats_text)

    def update_model_info(self, model_name, clusters, categories, status):
        """Actualizar información del modelo"""
        info_text = f"""🤖 Información del Modelo:

📋 Modelo: {model_name}
🎯 Clusters: {clusters}
📂 Categorías: {categories}
⚡ Estado: {status}

🔧 Método: Machine Learning
🎨 Colores: Verde/Rojo"""

        self.model_info_label.setText(info_text)

    def update_view_stats(self, view_type):
        """Actualizar estadísticas según el tipo de vista"""
        self.current_view = view_type

        # Re-actualizar con los mismos datos pero diferente vista
        self.update_stats(
            self.total_packets, self.classification_counts, self.current_view
        )

    def get_stats_summary(self):
        """Obtener resumen de estadísticas"""
        return {
            "total": self.total_packets,
            "normal": self.classification_counts.get("Normal", 0),
            "anomalo": self.classification_counts.get("Anómalo", 0),
            "view": self.current_view,
            "timestamp": time.time(),
        }
