"""Configuraciones globales del sistema"""

# Configuración del modelo
MODEL_PATH = "kmeans_model_improved.pkl"
SCALER_PATH = "scaler_kmeans_improved.pkl"

# Configuración de flujos
FLOW_TIMEOUT = 60
MAX_PACKETS_PER_TABLE = 1000
CLEANUP_INTERVAL = 100

# Configuración de red
PACKET_FILTER = "ip"
SNIFF_TIMEOUT = None

# Configuración de GUI
WINDOW_TITLE = "Sistema de Detección de Anomalías en Red - K-Means (2 Categorías)"
WINDOW_SIZE = (1400, 800)
STATS_UPDATE_INTERVAL = 1000  # ms
