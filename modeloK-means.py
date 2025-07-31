#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup rapido con NSL-KDD para mejorar la deteccion de anomalias
Ejecutar: python quick_dataset_setup.py
Version compatible con Windows
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.cluster import KMeans
import joblib
import urllib.request
import os
import sys


def download_nsl_kdd():
    """Descargar NSL-KDD dataset"""
    print("[INFO] Descargando NSL-KDD...")

    urls = {
        "train": "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt",
        "test": "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt",
    }

    files = {}
    for name, url in urls.items():
        filename = f"NSL_KDD_{name}.txt"
        if not os.path.exists(filename):
            print(f"Descargando {name}...")
            try:
                urllib.request.urlretrieve(url, filename)
                print(f"[OK] {filename} descargado")
            except Exception as e:
                print(f"[ERROR] Error descargando {name}: {e}")
                return None
        else:
            print(f"[OK] {filename} ya existe")
        files[name] = filename

    return files


def prepare_nsl_kdd(train_file, test_file):
    """Preparar NSL-KDD para K-Means"""
    print("[INFO] Preparando NSL-KDD...")

    # Nombres de columnas NSL-KDD
    column_names = [
        "duration",
        "protocol_type",
        "service",
        "flag",
        "src_bytes",
        "dst_bytes",
        "land",
        "wrong_fragment",
        "urgent",
        "hot",
        "num_failed_logins",
        "logged_in",
        "num_compromised",
        "root_shell",
        "su_attempted",
        "num_root",
        "num_file_creations",
        "num_shells",
        "num_access_files",
        "num_outbound_cmds",
        "is_host_login",
        "is_guest_login",
        "count",
        "srv_count",
        "serror_rate",
        "srv_serror_rate",
        "rerror_rate",
        "srv_rerror_rate",
        "same_srv_rate",
        "diff_srv_rate",
        "srv_diff_host_rate",
        "dst_host_count",
        "dst_host_srv_count",
        "dst_host_same_srv_rate",
        "dst_host_diff_srv_rate",
        "dst_host_same_src_port_rate",
        "dst_host_srv_diff_host_rate",
        "dst_host_serror_rate",
        "dst_host_srv_serror_rate",
        "dst_host_rerror_rate",
        "dst_host_srv_rerror_rate",
        "attack",
        "level",
    ]

    # Leer archivos
    print("[INFO] Cargando datos...")
    train_df = pd.read_csv(train_file, names=column_names, header=None)
    test_df = pd.read_csv(test_file, names=column_names, header=None)

    # Combinar train y test
    df = pd.concat([train_df, test_df], ignore_index=True)

    print(f"Total registros: {len(df)}")
    print("Tipos de ataques:")
    print(df["attack"].value_counts().head(10))

    return df


def create_flow_features(df):
    """Crear caracteristicas compatibles con tu modelo actual"""
    print("[INFO] Creando caracteristicas de flujo...")

    # Mapear caracteristicas NSL-KDD a las de tu modelo
    flow_features = pd.DataFrame()

    # Flow Duration - usar 'duration'
    flow_features["flow_duration"] = df["duration"]

    # Total Fwd Packets - aproximar con 'count'
    flow_features["total_fwd_packets"] = df["count"]

    # Total Backward Packets - aproximar
    flow_features["total_bwd_packets"] = df["srv_count"]

    # Flow IAT Mean - aproximar con srv_serror_rate
    flow_features["flow_iat_mean"] = df["serror_rate"]

    # Flow IAT Std - aproximar con srv_rerror_rate
    flow_features["flow_iat_std"] = df["rerror_rate"]

    # Packet Length Mean - usar src_bytes/count
    flow_features["packet_length_mean"] = np.where(
        df["count"] > 0, df["src_bytes"] / df["count"], df["src_bytes"]
    )

    # Packet Length Std - aproximar con dst_bytes
    flow_features["packet_length_std"] = np.log1p(df["dst_bytes"])

    # Flow Packets/s - aproximar
    flow_features["flow_packets_per_sec"] = np.where(
        df["duration"] > 0, df["count"] / (df["duration"] + 0.001), df["count"] * 1000
    )

    # Etiquetas (Normal vs Anomalo)
    labels = df["attack"].apply(lambda x: "normal" if x == "normal" else "anomaly")

    return flow_features, labels


def train_improved_model(X, y):
    """Entrenar modelo K-Means mejorado"""
    print("[INFO] Entrenando modelo K-Means mejorado...")

    # Limpiar datos
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())

    print(f"Datos limpios: {len(X)} registros, {len(X.columns)} caracteristicas")

    # Normalizar
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Entrenar K-Means con 3 clusters
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    # Analizar resultados
    analyze_clustering_results(clusters, y)

    # Guardar modelo mejorado
    joblib.dump(kmeans, "kmeans_model_improved.pkl")
    joblib.dump(scaler, "scaler_kmeans_improved.pkl")

    print("[OK] Modelo mejorado guardado!")
    return kmeans, scaler


def analyze_clustering_results(clusters, labels):
    """Analizar calidad del clustering"""
    print("\n[ANALISIS] RESULTADOS DE CLUSTERING")
    print("=" * 40)

    df_analysis = pd.DataFrame({"cluster": clusters, "label": labels})

    # Analisis por cluster
    for cluster_id in sorted(df_analysis["cluster"].unique()):
        cluster_data = df_analysis[df_analysis["cluster"] == cluster_id]

        print(f"\nCluster {cluster_id}:")
        print(f"   Tamano: {len(cluster_data)} registros")

        label_counts = cluster_data["label"].value_counts()
        for label, count in label_counts.items():
            percentage = (count / len(cluster_data)) * 100
            print(f"   {label}: {count} ({percentage:.1f}%)")

        # Determinar si es cluster normal o anomalo
        normal_pct = (cluster_data["label"] == "normal").mean() * 100
        cluster_type = "NORMAL" if normal_pct > 50 else "ANOMALO"
        print(f"   -> Tipo sugerido: {cluster_type}")


def create_mapping_file():
    """Crear archivo de mapeo de clusters"""
    mapping_info = """
# MAPEO DE CLUSTERS SUGERIDO
# Despues del entrenamiento, actualiza tu codigo con:

# Si Cluster 0 tiene mayoria de ataques -> Anomalo
# Si Cluster 1 tiene mayoria normal -> Normal  
# Si Cluster 2 es mixto -> Sospechoso

# En tu codigo PacketSniffer, cambia:
clasificacion = "Normal" if cluster == 1 else "ANOMALO"

# Por algo como:
cluster_mapping = {
    0: "ANOMALO",
    1: "Normal", 
    2: "Sospechoso"
}
clasificacion = cluster_mapping.get(cluster, "Desconocido")
"""

    # Escribir con encoding UTF-8 para evitar problemas
    with open("cluster_mapping_guide.txt", "w", encoding="utf-8") as f:
        f.write(mapping_info)

    print("[OK] Guia de mapeo guardada en: cluster_mapping_guide.txt")


def main():
    print("SETUP RAPIDO PARA MEJORAR DETECCION DE ANOMALIAS")
    print("=" * 60)

    # Paso 1: Descargar dataset
    print("\n1. DESCARGA DE DATASET")
    files = download_nsl_kdd()
    if not files:
        print("[ERROR] Error en descarga. Saliendo...")
        return

    # Paso 2: Preparar datos
    print("\n2. PREPARACION DE DATOS")
    df = prepare_nsl_kdd(files["train"], files["test"])

    # Paso 3: Crear caracteristicas
    print("\n3. CREACION DE CARACTERISTICAS")
    X, y = create_flow_features(df)

    # Paso 4: Entrenar modelo
    print("\n4. ENTRENAMIENTO DEL MODELO")
    kmeans, scaler = train_improved_model(X, y)

    # Paso 5: Crear guia
    print("\n5. CREACION DE GUIA")
    create_mapping_file()

    print("\n[SUCCESS] SETUP COMPLETADO!")
    print("=" * 40)
    print("Archivos generados:")
    print("   - kmeans_model_improved.pkl")
    print("   - scaler_kmeans_improved.pkl")
    print("   - cluster_mapping_guide.txt")
    print("\nPROXIMOS PASOS:")
    print("1. Copia los archivos .pkl sobre los originales")
    print("2. Revisa cluster_mapping_guide.txt")
    print("3. Actualiza el mapeo en tu codigo")
    print("4. Prueba el sistema mejorado!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n[ERROR] Error durante el proceso: {e}")
        print("Instala dependencias: pip install pandas scikit-learn numpy")
        import traceback

        traceback.print_exc()
