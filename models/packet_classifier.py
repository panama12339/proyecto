"""Clasificadores de paquetes"""

import numpy as np
from config.cluster_mapping import CLUSTER_MAPPING


class SimplePacketClassifier:
    """Clasificador heurístico simple"""

    def __init__(self):
        self.normal_ranges = {
            "packet_size": (20, 1500),
            "common_ports": {
                "TCP": [80, 443, 22, 21, 23, 25, 53, 110, 143, 993, 995],
                "UDP": [53, 67, 68, 123, 161, 162, 514],
            },
        }

    def is_suspicious_port(self, port, protocol):
        """Verificar si un puerto es sospechoso"""
        common_ports = self.normal_ranges["common_ports"].get(protocol, [])

        suspicious_conditions = [
            port > 49152,
            port in [1337, 31337, 12345, 54321],
            port < 1024 and port not in common_ports,
        ]

        return any(suspicious_conditions)

    def classify_single_packet(self, packet_size, src_port, dst_port, protocol):
        """Clasificación simple basada en heurísticas"""
        suspicion_score = 0

        min_size, max_size = self.normal_ranges["packet_size"]
        if packet_size < min_size or packet_size > max_size:
            suspicion_score += 1

        if self.is_suspicious_port(src_port, protocol):
            suspicion_score += 1
        if self.is_suspicious_port(dst_port, protocol):
            suspicion_score += 1

        if packet_size < 64 or packet_size > 1400:
            suspicion_score += 0.5

        return "Anómalo" if suspicion_score >= 1 else "Normal"


class KMeansClassifier:
    """Clasificador usando K-Means"""

    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler

    def classify(self, features):
        """Clasificar usando K-Means"""
        try:
            input_features = np.array([features])
            input_scaled = self.scaler.transform(input_features)
            cluster = self.model.predict(input_scaled)[0]

            clasificacion = CLUSTER_MAPPING.get(cluster, "Anómalo")
            method = f"K-Means (C{cluster})"

            return clasificacion, method
        except Exception as e:
            return None, f"Error: {str(e)[:15]}"
