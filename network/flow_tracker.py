"""Seguimiento y análisis de flujos de red"""

import statistics
from collections import defaultdict


class FlowTracker:
    """Clase para rastrear y calcular estadísticas de flujos de red"""

    def __init__(self, flow_timeout=60):
        self.flows = defaultdict(
            lambda: {
                "packets": [],
                "start_time": None,
                "last_seen": None,
                "fwd_packets": 0,
                "bwd_packets": 0,
                "packet_sizes": [],
                "inter_arrival_times": [],
            }
        )
        self.flow_timeout = flow_timeout

    def get_flow_key(self, src_ip, dst_ip, src_port, dst_port, protocol):
        """Generar clave única para el flujo"""
        return f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-{protocol}"

    def add_packet(
        self, src_ip, dst_ip, src_port, dst_port, protocol, packet_size, timestamp
    ):
        """Agregar paquete al flujo correspondiente"""
        flow_key = self.get_flow_key(src_ip, dst_ip, src_port, dst_port, protocol)
        flow = self.flows[flow_key]

        if flow["start_time"] is None:
            flow["start_time"] = timestamp
            flow["fwd_packets"] = 1
        else:
            if flow["last_seen"] is not None:
                iat = timestamp - flow["last_seen"]
                flow["inter_arrival_times"].append(iat)
            flow["fwd_packets"] += 1

        flow["last_seen"] = timestamp
        flow["packets"].append(
            {"timestamp": timestamp, "size": packet_size, "src": src_ip, "dst": dst_ip}
        )
        flow["packet_sizes"].append(packet_size)

        return flow_key

    def calculate_flow_features(self, flow_key, use_defaults=True):
        """Calcular características del flujo para el modelo"""
        if flow_key not in self.flows:
            return None

        flow = self.flows[flow_key]

        if len(flow["packets"]) < 2 and not use_defaults:
            return None

        # Calcular características del flujo
        flow_duration = (
            flow["last_seen"] - flow["start_time"]
            if len(flow["packets"]) >= 2
            else 0.001
        )

        total_fwd_packets = flow["fwd_packets"]
        total_bwd_packets = max(0, len(flow["packets"]) - flow["fwd_packets"])

        # IAT estadísticas
        if len(flow["inter_arrival_times"]) > 0:
            flow_iat_mean = statistics.mean(flow["inter_arrival_times"])
            flow_iat_std = (
                statistics.stdev(flow["inter_arrival_times"])
                if len(flow["inter_arrival_times"]) > 1
                else 0
            )
        else:
            flow_iat_mean = 0.0
            flow_iat_std = 0.0

        # Packet length estadísticas
        if len(flow["packet_sizes"]) > 0:
            packet_length_mean = statistics.mean(flow["packet_sizes"])
            packet_length_std = (
                statistics.stdev(flow["packet_sizes"])
                if len(flow["packet_sizes"]) > 1
                else 0
            )
        else:
            packet_length_mean = 0
            packet_length_std = 0

        # Flow packets/s
        flow_packets_per_sec = (
            len(flow["packets"]) / flow_duration if flow_duration > 0 else 0
        )

        return [
            flow_duration,
            total_fwd_packets,
            total_bwd_packets,
            flow_iat_mean,
            flow_iat_std,
            packet_length_mean,
            packet_length_std,
            flow_packets_per_sec,
        ]

    def cleanup_old_flows(self, current_time):
        """Limpiar flujos antiguos"""
        to_remove = [
            flow_key
            for flow_key, flow in self.flows.items()
            if current_time - flow["last_seen"] > self.flow_timeout
        ]

        for flow_key in to_remove:
            del self.flows[flow_key]
