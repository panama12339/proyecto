"""
Componente Barra Lateral (Sidebar)
Archivo: gui/components/sidebar.py
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from gui.components.stats_panel import StatsPanel


class Sidebar(QWidget):
    """Barra lateral con navegación y estadísticas"""

    # Señales
    view_changed = pyqtSignal(str)  # Emitir cuando cambie la vista

    def __init__(self):
        super().__init__()
        self.current_view = "all"
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Configurar interfaz de la barra lateral"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Logo/Título
        self.create_logo(layout)

        # Botones de navegación
        self.create_navigation_buttons(layout)

        # Panel de estadísticas integrado
        self.stats_panel = StatsPanel()
        layout.addWidget(self.stats_panel)

    def create_logo(self, layout):
        """Crear logo/título de la aplicación"""
        logo = QLabel("AnomDetect v2.0")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Arial", 14, QFont.Bold))
        logo.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                margin: 10px;
                padding: 15px;
                background-color: white;
                border-radius: 8px;
                border: 2px solid #3498db;
            }
        """
        )
        layout.addWidget(logo)

    def create_navigation_buttons(self, layout):
        """Crear botones de navegación"""
        # Configuración de botones
        buttons_config = [
            ("inicio", "Inicio", "#4CAF50", self.on_inicio_clicked),
            ("captura", "Captura", "#4CAF50", self.on_captura_clicked),
            ("anomalo", "Tráfico Anómalo", "#f44336", self.on_anomalo_clicked),
            ("alertas", "Alertas", "#4CAF50", self.on_alertas_clicked),
            ("config", "Configuración", "#4CAF50", self.on_config_clicked),
        ]

        # Crear y almacenar botones
        self.buttons = {}

        for btn_id, text, color, callback in buttons_config:
            btn = QPushButton(text)
            btn.setMinimumHeight(45)
            btn.setObjectName(btn_id)
            btn.clicked.connect(callback)

            # Estilo especial para botón anómalo
            if btn_id == "anomalo":
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border: none;
                        padding: 8px;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: #d32f2f;
                    }}
                    QPushButton:pressed {{
                        background-color: #b71c1c;
                    }}
                """
                )
            else:
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border: none;
                        padding: 8px;
                        border-radius: 4px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #45a049;
                    }}
                """
                )

            self.buttons[btn_id] = btn
            layout.addWidget(btn)

        # Establecer botón inicial como activo
        self.update_button_styles("inicio")

    def setup_connections(self):
        """Configurar conexiones de señales"""
        pass  # Las conexiones se hacen en create_navigation_buttons

    def on_inicio_clicked(self):
        """Manejar clic en botón Inicio"""
        self.switch_to_view("all", "inicio")

    def on_captura_clicked(self):
        """Manejar clic en botón Captura"""
        self.switch_to_view("all", "captura")

    def on_anomalo_clicked(self):
        """Manejar clic en botón Tráfico Anómalo"""
        self.switch_to_view("anomalous", "anomalo")

    def on_alertas_clicked(self):
        """Manejar clic en botón Alertas"""
        # Placeholder - podrías mostrar una vista de alertas
        print("[INFO] Vista de Alertas - Funcionalidad futura")

    def on_config_clicked(self):
        """Manejar clic en botón Configuración"""
        # Placeholder - podrías mostrar configuraciones
        print("[INFO] Vista de Configuración - Funcionalidad futura")

    def switch_to_view(self, view_type, button_id):
        """Cambiar a una vista específica"""
        if self.current_view != view_type:
            self.current_view = view_type
            self.view_changed.emit(view_type)

        # Actualizar estilos de botones
        self.update_button_styles(button_id)

        # Actualizar panel de estadísticas
        self.stats_panel.update_view_stats(view_type)

    def update_button_styles(self, active_button_id):
        """Actualizar estilos de botones según el activo"""
        for btn_id, btn in self.buttons.items():
            if btn_id == active_button_id:
                # Estilo para botón activo
                if btn_id == "anomalo":
                    btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #d32f2f;
                            color: white;
                            border: 2px solid #ffffff;
                            padding: 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                        }
                    """
                    )
                else:
                    btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: 2px solid #ffffff;
                            padding: 8px;
                            border-radius: 4px;
                            font-weight: bold;
                        }
                    """
                    )
            else:
                # Estilo para botones inactivos
                if btn_id == "anomalo":
                    btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: none;
                            padding: 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #d32f2f;
                        }
                    """
                    )
                else:
                    btn.setStyleSheet(
                        """
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
                    """
                    )

    def update_stats(self, stats_data):
        """Actualizar estadísticas en el panel"""
        total = stats_data.get("total_packets", 0)
        classification_counts = stats_data.get(
            "classification_counts", {"Normal": 0, "Anómalo": 0}
        )
        current_view = stats_data.get("current_view", "all")
        anomaly_table_count = stats_data.get("anomaly_table_count", 0)

        self.stats_panel.update_stats(
            total, classification_counts, current_view, anomaly_table_count
        )

    def get_current_view(self):
        """Obtener vista actual"""
        return self.current_view

    def set_model_info(self, model_name, clusters, categories, status):
        """Establecer información del modelo"""
        self.stats_panel.update_model_info(model_name, clusters, categories, status)
