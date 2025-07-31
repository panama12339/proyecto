"""Captura y procesamiento de paquetes de red"""

import time
from PyQt5.QtCore import QThread, pyqtSignal
from scapy.all import sniff, IP, TCP, UDP

from models.model_loader import ModelLoader
from models.packet_classifier import SimplePacketClassifier, KMeansClassifier
from network.flow_tracker import FlowTracker
from config.settings import PACKET_FILTER, CLEANUP_INTERVAL


class PacketSniffer(QThread):
    packet_signal = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.packet_count = 0

        # Inicializar componentes
        model_loader = ModelLoader()
        self.flow_tracker = FlowTracker()
        self.simple_classifier = SimplePacketClassifier()
        self.kmeans_classifier = KMeansClassifier(
            model_loader.get_model(), model_loader.get_scaler()
        )

    def run(self):
        """Iniciar captura de paquetes"""
        print("[INFO] Iniciando captura de paquetes...")
        sniff(prn=self.process_packet, store=False, filter=PACKET_FILTER)

    def process_packet(self, packet):
        """Procesar paquete capturado"""
        try:
            if IP in packet:
                current_time = time.time()
                self.packet_count += 1

                # Extraer información del paquete
                packet_info = self._extract_packet_info(packet, current_time)

                # Clasificar paquete
                classification = self._classify_packet(packet_info)

                # Limpiar flujos antiguos periódicamente
                if self.packet_count % CLEANUP_INTERVAL == 0:
                    self.flow_tracker.cleanup_old_flows(current_time)

                # Emitir señal para GUI
                data = (*packet_info, classification)
                self.packet_signal.emit(data)

        except Exception as e:
            print(f"[ERROR] Error procesando paquete: {e}")

    def _extract_packet_info(self, packet, current_time):
        """Extraer información básica del paquete"""
        timestamp = round(current_time - self.start_time, 6)
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        packet_length = len(packet)

        if TCP in packet:
            protocol = "TCP"
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        elif UDP in packet:
            protocol = "UDP"
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
        else:
            protocol = str(packet[IP].proto)
            src_port = 0
            dst_port = 0

        info = f"{src_port} -> {dst_port} [{protocol}]"

        return (
            self.packet_count,
            timestamp,
            src_ip,
            dst_ip,
            protocol,
            packet_length,
            info,
        )

    def _classify_packet(self, packet_info):
        """Clasificar paquete usando diferentes métodos"""
        _, timestamp, src_ip, dst_ip, protocol, packet_length, info = packet_info

        # Obtener puertos desde info
        try:
            src_port = int(info.split(" -> ")[0])
            dst_port = int(info.split(" -> ")[1].split(" [")[0])
        except:
            src_port = dst_port = 0

        # Agregar a flow tracker
        flow_key = self.flow_tracker.add_packet(
            src_ip, dst_ip, src_port, dst_port, protocol, packet_length, timestamp
        )

        # Intentar clasificación con K-Means
        flow_features = self.flow_tracker.calculate_flow_features(flow_key)

        if flow_features is not None:
            clasificacion, method = self.kmeans_classifier.classify(flow_features)
            if clasificacion is None:
                clasificacion = self.simple_classifier.classify_single_packet(
                    packet_length, src_port, dst_port, protocol
                )
                method = "Heurística (Error K-Means)"
        else:
            # Fallback a clasificación heurística
            clasificacion = self.simple_classifier.classify_single_packet(
                packet_length, src_port, dst_port, protocol
            )
            method = "Heurística (Fallback)"

        return f"{clasificacion} ({method})"
