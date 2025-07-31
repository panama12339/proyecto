"""Ventana principal de la aplicación"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import QTimer

from gui.components.sidebar import Sidebar
from .components.packet_table import PacketTableManager
from gui.components.stats_panel import StatsPanel
from gui.styles.styles import MAIN_STYLESHEET
from network.packet_sniffer import PacketSniffer

# ✅ CORRECTO
from config.settings import WINDOW_TITLE, WINDOW_SIZE, STATS_UPDATE_INTERVAL


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        self.start_sniffer()

    def setup_window(self):
        """Configurar ventana principal"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, *WINDOW_SIZE)
        self.setStyleSheet(MAIN_STYLESHEET)

    def setup_ui(self):
        """Configurar interfaz de usuario"""
        main_layout = QHBoxLayout(self)

        # Componentes principales
        self.sidebar = Sidebar()
        self.table_manager = PacketTableManager()
        self.stats_panel = StatsPanel()

        # Layout
        main_layout.addWidget(self.sidebar, 1)
        main_layout.addWidget(self.table_manager, 4)

    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Timer para estadísticas
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(STATS_UPDATE_INTERVAL)

        # Conexiones de botones
        self.sidebar.view_changed.connect(self.table_manager.switch_view)

    def start_sniffer(self):
        """Iniciar captura de paquetes"""
        self.sniffer = PacketSniffer()
        self.sniffer.packet_signal.connect(self.table_manager.add_packet)
        self.sniffer.start()

    def update_stats(self):
        """Actualizar estadísticas"""
        stats = self.table_manager.get_statistics()
        self.sidebar.update_stats(stats)
